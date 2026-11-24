import os
import time
from typing import Any, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx

app = FastAPI(title="PMCS Job Discovery & Career Intelligence API", version="1.6.0")

# Izinkan frontend GitHub Pages kamu (dan localhost saat uji coba lokal)
ALLOWED_ORIGINS = [
    "https://devlabs-id.github.io",
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Baca kredensial dari environment variables di server backend (JANGAN di-hardcode)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
JOB104_API_KEY = os.getenv("JOB104_API_KEY")
JOB104_API_URL = os.getenv("JOB104_API_URL")

GEMINI_CANDIDATE_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash",
]

# Data sampel fallback (dipakai bila 104 live fetch terblokir atau belum tersedia)
FALLBACK_JOBS: list[dict[str, Any]] = [
    {
        "job_id": "104-sample-001",
        "source": "104",
        "source_url": "https://www.104.com.tw/",
        "job_title_original": "資深產品經理 Senior Product Manager (SaaS 平台)",
        "company_name_original": "雲脈數位科技股份有限公司",
        "job_description_original": (
            "1. 負責 B2B 雲端協作產品之長期產品策略與季度 Roadmap 規劃。\n"
            "2. 進行企業客戶深度訪談與市場競品分析，將商業痛點轉化為具體 PRD 與 User Story。\n"
            "3. 依據數據指標動態調整功能開發優先順序。"
        ),
    }
]


class AnalyzeJobRequest(BaseModel):
    job_id: str
    job_title_original: str
    job_description_original: str
    language: Literal["en", "zh-TW"] = "en"


class CareerFitRequest(BaseModel):
    narrative: str = Field(..., min_length=1)
    target_job_title: str
    target_jd_summary: str
    language: Literal["en", "zh-TW"] = "en"


class AssistantRequest(BaseModel):
    question: str = Field(..., min_length=1)
    language: Literal["en", "zh-TW"] = "en"
    selected_job: Optional[dict[str, Any]] = None


def call_gemini_with_fallback(
    system_prompt: str,
    user_prompt: str,
    json_mode: bool = False,
) -> tuple[str, str]:
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is not configured in backend environment variables.",
        )

    combined_prompt = f"{system_prompt}\n\n{user_prompt}".strip()
    last_error: str = "Unknown Gemini API error"

    with httpx.Client(timeout=60.0) as client:
        for model_name in GEMINI_CANDIDATE_MODELS:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model_name}:generateContent?key={GEMINI_API_KEY}"
            )
            gen_config: dict[str, Any] = {"temperature": 0.25}
            if json_mode:
                gen_config["responseMimeType"] = "application/json"

            for attempt in range(2):
                try:
                    resp = client.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        json={
                            "contents": [{"parts": [{"text": combined_prompt}]}],
                            "generationConfig": gen_config,
                        },
                    )
                    if resp.status_code == 404:
                        last_error = f"Model {model_name} returned 404 Not Found"
                        break
                    if resp.status_code == 429:
                        last_error = f"Model {model_name} rate limited (429)"
                        time.sleep(5 * (attempt + 1))
                        continue
                    resp.raise_for_status()
                    payload = resp.json()
                    text_out = payload["candidates"][0]["content"]["parts"][0]["text"]
                    return text_out, model_name
                except Exception as exc:
                    last_error = f"{model_name}: {exc}"
                    time.sleep(2)

    raise HTTPException(status_code=502, detail=f"Gemini API failed: {last_error}")


async def fetch_104_vacancies(keyword: str = "Product Manager", page: int = 1) -> dict[str, Any]:
    """Mengambil data lowongan langsung dari endpoint pencarian publik www.104.com.tw."""
    search_keyword = keyword.strip() or "Product Manager"
    url = "https://www.104.com.tw/jobs/search/api/jobs"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.104.com.tw/jobs/search/",
        "Accept": "application/json, text/plain, */*",
    }
    params = {
        "keyword": search_keyword,
        "page": page,
        "pagesize": 10,
        "order": 15,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            payload = resp.json()

        raw_list = payload.get("data", []) if isinstance(payload, dict) else []
        jobs = []
        for item in raw_list:
            job_link = item.get("link", {}).get("job", "")
            full_url = (
                f"https:{job_link}"
                if job_link.startswith("//")
                else (job_link or "https://www.104.com.tw/")
            )
            jobs.append(
                {
                    "job_id": str(item.get("jobNo", "")),
                    "source": "104",
                    "source_url": full_url,
                    "job_title_original": item.get("jobName", ""),
                    "company_name_original": item.get("custName", ""),
                    "location": item.get("jobAddrNoDesc", ""),
                    "salary_display": item.get("salaryDesc", "Not provided"),
                    "posting_date": item.get("appearDate", ""),
                    "job_description_original": item.get("description", ""),
                }
            )

        return {
            "source_mode": "104_live_web",
            "keyword": search_keyword,
            "total_fetched": len(jobs),
            "jobs": jobs if jobs else FALLBACK_JOBS,
        }
    except Exception as exc:
        return {
            "source_mode": "fallback_sample",
            "note": f"104 live fetch fallback triggered: {exc}",
            "jobs": FALLBACK_JOBS,
        }


@app.get("/health")
def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "gemini_configured": bool(GEMINI_API_KEY),
        "job104_configured": bool(JOB104_API_URL and JOB104_API_KEY),
    }


@app.get("/api/jobs/104")
async def get_104_jobs(keyword: str = "", page: int = 1) -> dict[str, Any]:
    try:
        return await fetch_104_vacancies(keyword=keyword, page=page)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"104 API request failed: {exc}") from exc


@app.post("/api/analyze-job")
def analyze_job(req: AnalyzeJobRequest) -> dict[str, Any]:
    system_prompt = (
        "You are a career intelligence analyst for PM/PjM roles. "
        "Classify roles by primary management object and ultimate responsibility into: "
        "PM, PjM, Hybrid, Unclear, or Other (never by job title alone). "
        "Never invent facts missing from the JD. Respond strictly in JSON with keys: "
        "classification, classification_reason, summary, responsibilities_evidence, "
        "explicit_competencies, inferred_competencies."
    )
    user_prompt = (
        f"Output language: {req.language}\n"
        f"Job ID: {req.job_id}\n"
        f"Original Title: {req.job_title_original}\n"
        f"Original JD:\n{req.job_description_original}"
    )
    raw_json, used_model = call_gemini_with_fallback(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        json_mode=True,
    )
    return {
        "job_id": req.job_id,
        "model": used_model,
        "analysis_raw_json": raw_json,
    }


@app.post("/api/career-fit")
def career_fit(req: CareerFitRequest) -> dict[str, Any]:
    system_prompt = (
        "Compare the user's self-reported experience narrative against target vacancy requirements. "
        "Categorize points as Matched, Partially Matched, Not Demonstrated, or Insufficient Evidence. "
        "Explicitly state this is an exploratory comparison, not a hiring prediction or verified ability score."
    )
    user_prompt = (
        f"Language: {req.language}\n"
        f"Target Role: {req.target_job_title}\n"
        f"Vacancy Summary: {req.target_jd_summary}\n"
        f"User Narrative: {req.narrative}"
    )
    assessment, used_model = call_gemini_with_fallback(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        json_mode=False,
    )
    return {"model": used_model, "assessment": assessment}


@app.post("/api/assistant")
def assistant_chat(req: AssistantRequest) -> dict[str, Any]:
    context_block = (
        f"Selected Vacancy Context: {req.selected_job}"
        if req.selected_job
        else "No vacancy selected. Answer using general PM/PjM career guidance."
    )
    system_prompt = (
        "You are the PMCS AI Career Assistant. Clearly state whether your answer uses the selected vacancy "
        "or general PM/PjM career guidance. Never fabricate details absent from the source JD."
    )
    user_prompt = (
        f"Language: {req.language}\n"
        f"{context_block}\n"
        f"Question: {req.question}"
    )
    reply, _ = call_gemini_with_fallback(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        json_mode=False,
    )
    return {
        "context_mode": "selected_vacancy" if req.selected_job else "general_career",
        "reply": reply,
    }
