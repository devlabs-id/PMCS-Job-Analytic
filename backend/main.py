import os
from typing import Any, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from openai import OpenAI

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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
JOB104_API_KEY = os.getenv("JOB104_API_KEY")
JOB104_API_URL = os.getenv("JOB104_API_URL")  # Isi sesuai dokumentasi resmi 104 bila sudah tersedia
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Data sampel fallback (dipakai bila JOB104_API_URL belum dikonfigurasi)
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


async def fetch_104_vacancies(keyword: str = "", page: int = 1) -> dict[str, Any]:
    """Mengambil data lowongan dari 104 Job Bank API di sisi backend."""
    if not JOB104_API_URL:
        return {
            "source_mode": "fallback_sample",
            "note": "JOB104_API_URL not yet configured; returning sample record.",
            "jobs": FALLBACK_JOBS,
        }

    headers: dict[str, str] = {"Accept": "application/json"}
    if JOB104_API_KEY:
        headers["Authorization"] = f"Bearer {JOB104_API_KEY}"

    params = {"keyword": keyword, "page": page}
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(JOB104_API_URL, headers=headers, params=params)
        resp.raise_for_status()
        payload = resp.json()

    return {
        "source_mode": "104_api",
        "jobs": payload if isinstance(payload, list) else payload.get("data", []),
    }


def require_openai() -> OpenAI:
    if not openai_client:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not configured in backend environment variables.",
        )
    return openai_client


@app.get("/health")
def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "openai_configured": bool(OPENAI_API_KEY),
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
    client = require_openai()
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
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return {
        "job_id": req.job_id,
        "model": OPENAI_MODEL,
        "analysis_raw_json": completion.choices[0].message.content,
    }


@app.post("/api/career-fit")
def career_fit(req: CareerFitRequest) -> dict[str, Any]:
    client = require_openai()
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
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return {"model": OPENAI_MODEL, "assessment": completion.choices[0].message.content}


@app.post("/api/assistant")
def assistant_chat(req: AssistantRequest) -> dict[str, Any]:
    client = require_openai()
    context_block = (
        f"Selected Vacancy Context: {req.selected_job}"
        if req.selected_job
        else "No vacancy selected. Answer using general PM/PjM career guidance."
    )
    system_prompt = (
        "You are the PMCS AI Career Assistant. Clearly state whether your answer uses the selected vacancy "
        "or general PM/PjM career guidance. Never fabricate details absent from the source JD."
    )
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Language: {req.language}\n{context_block}\nQuestion: {req.question}"},
        ],
    )
    return {
        "context_mode": "selected_vacancy" if req.selected_job else "general_career",
        "reply": completion.choices[0].message.content,
    }
