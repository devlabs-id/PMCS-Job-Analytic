import json
import os
import re
import time
from typing import Any, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx

app = FastAPI(title="PMCS Job Discovery & Career Intelligence API", version="1.8.2")

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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

JOB104_API_KEY = os.getenv("JOB104_API_KEY")
JOB104_API_URL = os.getenv("JOB104_API_URL")

_MODEL_CACHE: dict[str, tuple[float, list[str]]] = {}


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


class CareerMatchTopRequest(BaseModel):
    narrative: str = Field(..., min_length=1)
    jobs: list[dict[str, Any]] = Field(..., min_length=1)
    language: Literal["en", "zh-TW"] = "en"


class AssistantRequest(BaseModel):
    question: str = Field(..., min_length=1)
    language: Literal["en", "zh-TW"] = "en"
    context: Optional[str] = None
    selected_job: Optional[dict[str, Any]] = None


def _clean_json_text(raw_text: str) -> str:
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    return cleaned


def _format_three_paragraphs(raw_text: str, language: str) -> str:
    text = str(raw_text or "").strip()
    if not text:
        return ""

    try:
        parsed = json.loads(_clean_json_text(text))
        if isinstance(parsed, dict) and isinstance(parsed.get("paragraphs"), list):
            items = [str(p).strip() for p in parsed["paragraphs"] if str(p).strip()]
            if len(items) >= 3:
                return "\n\n".join(items[:3])
    except Exception:
        pass

    blocks = [b.strip() for b in re.split(r"\n{2,}|\r?\n", text) if b.strip()]
    if len(blocks) >= 3:
        return "\n\n".join(blocks[:3])

    sentences = [s.strip() for s in re.split(r"(?<=[.!?。！？])\s+", text) if s.strip()]
    if len(sentences) >= 3:
        size = max(1, len(sentences) // 3)
        p1 = " ".join(sentences[:size])
        p2 = " ".join(sentences[size : size * 2])
        p3 = " ".join(sentences[size * 2 :])
        return "\n\n".join([p for p in (p1, p2, p3) if p])

    if language == "zh-TW":
        return "\n\n".join([
            text,
            "在職能與經驗對照上，建議將你過往專案中負責的協調對象、決策依據與推進步驟，與目標職缺的核心要求逐一連結，突顯可遷移的實務能力。",
            "作為後續準備方向，可補充具體的成果指標、工具運用或跨團隊合作細節，並針對該職缺最重視的關鍵任務整理 1 至 2 個完整案例。",
        ])

    return "\n\n".join([
        text,
        "In terms of competency alignment, connect the specific coordination, planning, or problem-solving steps in your experience directly to the core duties of the target role.",
        "As a practical next step, add concrete outcomes, tools used, or cross-team collaboration details, and prepare one or two clear examples tied to the vacancy's key priorities.",
    ])


def _get_cached_models(client: httpx.Client, provider: str) -> list[str]:
    now = time.time()
    cached = _MODEL_CACHE.get(provider)
    if cached and (now - cached[0]) < 1800 and cached[1]:
        return cached[1]

    models: list[str] = []
    try:
        if provider == "gemini" and GEMINI_API_KEY:
            r = client.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}",
                timeout=15.0,
            )
            if r.status_code == 200:
                for m in r.json().get("models", []):
                    name = m.get("name", "").replace("models/", "")
                    methods = m.get("supportedGenerationMethods", [])
                    if "generateContent" in methods and "gemini" in name.lower():
                        if not any(x in name.lower() for x in ("exp", "vision-old", "embedding")):
                            models.append(name)
                models.sort(
                    key=lambda x: (
                        0 if "2.5-flash" in x else (1 if "2.0-flash" in x else (2 if "flash" in x else 3)),
                        x,
                    )
                )
        elif provider == "groq" and GROQ_API_KEY:
            r = client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                timeout=15.0,
            )
            if r.status_code == 200:
                models = [
                    m["id"]
                    for m in r.json().get("data", [])
                    if m.get("id") and not any(b in m["id"].lower() for b in ("whisper", "guard", "tts", "embed"))
                ]
                models.sort(key=lambda x: (0 if "70b" in x else (1 if "llama" in x else 2), x))
        elif provider == "openrouter" and OPENROUTER_API_KEY:
            r = client.get("https://openrouter.ai/api/v1/models", timeout=15.0)
            if r.status_code == 200:
                for m in r.json().get("data", []):
                    mid = m.get("id", "")
                    if mid.endswith(":free") and not any(b in mid.lower() for b in ("vision", "vl", "embed", "audio")):
                        models.append(mid)
                models.sort(key=lambda x: (0 if any(k in x.lower() for k in ("llama", "qwen", "gemini", "mistral")) else 1, x))
        elif provider == "openai" and OPENAI_API_KEY:
            models = ["gpt-4o-mini"]
    except Exception:
        pass

    result = models[:4]
    if result:
        _MODEL_CACHE[provider] = (now, result)
    return result


def call_gemini_with_fallback(
    system_prompt: str,
    user_prompt: str,
    json_mode: bool = False,
) -> tuple[str, str]:
    if not any([GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, OPENAI_API_KEY]):
        raise HTTPException(status_code=503, detail="No AI provider API key configured.")

    combined_prompt = f"{system_prompt}\n\n{user_prompt}".strip()
    errors: list[str] = []

    with httpx.Client(timeout=35.0) as client:
        for model_name in _get_cached_models(client, "gemini"):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
                gen_config: dict[str, Any] = {"temperature": 0.25}
                if json_mode:
                    gen_config["responseMimeType"] = "application/json"
                resp = client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={"contents": [{"parts": [{"text": combined_prompt}]}], "generationConfig": gen_config},
                )
                if resp.status_code != 200:
                    errors.append(f"gemini:{model_name} HTTP {resp.status_code}")
                    continue
                text_out = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                if json_mode:
                    text_out = _clean_json_text(text_out)
                    json.loads(text_out)
                return text_out, f"gemini:{model_name}"
            except Exception as exc:
                errors.append(f"gemini:{model_name} {exc}")

        openai_providers = [
            ("groq", "https://api.groq.com/openai/v1/chat/completions", GROQ_API_KEY, {}),
            (
                "openrouter",
                "https://openrouter.ai/api/v1/chat/completions",
                OPENROUTER_API_KEY,
                {"HTTP-Referer": "https://devlabs-id.github.io/PMCS-Job-Analytic/", "X-Title": "PMCS-Job-Analytic"},
            ),
            ("openai", "https://api.openai.com/v1/chat/completions", OPENAI_API_KEY, {}),
        ]
        for pname, endpoint, key, extra in openai_providers:
            if not key:
                continue
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", **extra}
            for model_name in _get_cached_models(client, pname):
                try:
                    body: dict[str, Any] = {
                        "model": model_name,
                        "temperature": 0.25,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                    }
                    if json_mode and pname in ("groq", "openai"):
                        body["response_format"] = {"type": "json_object"}
                    resp = client.post(endpoint, headers=headers, json=body)
                    if resp.status_code != 200:
                        errors.append(f"{pname}:{model_name} HTTP {resp.status_code}")
                        continue
                    text_out = resp.json()["choices"][0]["message"]["content"]
                    if json_mode:
                        text_out = _clean_json_text(text_out)
                        json.loads(text_out)
                    return text_out, f"{pname}:{model_name}"
                except Exception as exc:
                    errors.append(f"{pname}:{model_name} {exc}")

    raise HTTPException(status_code=502, detail="All AI providers failed: " + " | ".join(errors[:8]))


@app.get("/health")
def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "gemini_configured": bool(GEMINI_API_KEY),
        "groq_configured": bool(GROQ_API_KEY),
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "openai_configured": bool(OPENAI_API_KEY),
        "job104_configured": bool(JOB104_API_URL and JOB104_API_KEY),
    }


@app.post("/api/analyze-job")
def analyze_job(req: AnalyzeJobRequest) -> dict[str, Any]:
    system_prompt = (
        "You are a career intelligence analyst for PM/PjM roles. "
        "Classify roles into PM, PjM, Hybrid, Unclear, or Other. Respond strictly in JSON with keys: "
        "classification, classification_reason, summary, responsibilities_evidence, "
        "explicit_competencies, inferred_competencies."
    )
    user_prompt = (
        f"Output language: {req.language}\n"
        f"Job ID: {req.job_id}\n"
        f"Original Title: {req.job_title_original}\n"
        f"Original JD:\n{req.job_description_original}"
    )
    raw_json, used_model = call_gemini_with_fallback(system_prompt, user_prompt, json_mode=True)
    return {"job_id": req.job_id, "model": used_model, "analysis_raw_json": raw_json}


@app.post("/api/career-fit")
def career_fit(req: CareerFitRequest) -> dict[str, Any]:
    system_prompt = (
        "You are a career fit advisor comparing a candidate's experience narrative against a 104 Job Bank vacancy. "
        "Write in the requested language ('en' -> English, 'zh-TW' -> Traditional Chinese). "
        "Structure your response into EXACTLY THREE clear, well-written narrative paragraphs separated by a blank line:\n"
        "Paragraph 1: Overall alignment & core strengths matched to the target role.\n"
        "Paragraph 2: Areas where evidence is partial or missing (Knowledge, Skills, Attitude) and how to frame existing experience.\n"
        "Paragraph 3: Concrete next steps for portfolio/resume preparation and role readiness.\n"
        "Do not use bullet points or numbered list prefixes inside paragraphs, and explicitly note this is an exploratory comparison rather than a hiring score."
    )
    user_prompt = (
        f"Language: {req.language}\n"
        f"Target Role: {req.target_job_title}\n"
        f"Vacancy Summary: {req.target_jd_summary}\n"
        f"User Narrative: {req.narrative}"
    )
    raw_assessment, used_model = call_gemini_with_fallback(system_prompt, user_prompt, json_mode=False)
    assessment = _format_three_paragraphs(raw_assessment, req.language)
    return {"model": used_model, "assessment": assessment}


@app.post("/api/career-match-top")
def career_match_top(req: CareerMatchTopRequest) -> dict[str, Any]:
    compact_jobs = [
        {
            "job_id": j.get("job_id"),
            "title": j.get("job_title_original"),
            "company": j.get("company_name_original"),
            "classification": j.get("classification"),
            "summary": j.get("summary_en") or j.get("summary_zh") or str(j.get("job_description_original", ""))[:300],
        }
        for j in req.jobs[:25]
    ]
    system_prompt = (
        "You are a career matching advisor. Rank the top 3 most suitable 104 Job Bank vacancies for the user's "
        "narrative (experience, knowledge, skills). Return ONLY valid JSON with key 'matches' (list of 3 objects), "
        "each having: 'job_id', 'fit_level' ('High Match' | 'Moderate Match' | 'Exploratory Match'), "
        "'matched_signals' (list of strings), and 'reason' (2-sentence explanation in the requested language)."
    )
    user_prompt = (
        f"Language: {req.language}\n"
        f"User Narrative: {req.narrative}\n"
        f"Available 104 Jobs: {json.dumps(compact_jobs, ensure_ascii=False)}"
    )
    raw_json, used_model = call_gemini_with_fallback(system_prompt, user_prompt, json_mode=True)
    return {"model": used_model, "matches_json": raw_json}


@app.post("/api/assistant")
def assistant_chat(req: AssistantRequest) -> dict[str, Any]:
    context_parts: list[str] = []
    if req.selected_job:
        context_parts.append(f"Selected Vacancy Context: {json.dumps(req.selected_job, ensure_ascii=False)}")
    if req.context:
        context_parts.append(f"Dataset & Platform Context: {req.context[:3500]}")
    context_block = "\n".join(context_parts) if context_parts else "No specific vacancy selected. Answer using general PM/PjM career guidance and platform details."

    system_prompt = (
        "You are the PMCS AI Career Assistant. Answer concisely and accurately in the requested language. "
        "Clearly state whether your answer uses a specific vacancy/dataset context or general PM/PjM career guidance. "
        "Never fabricate details absent from the provided context or source JD."
    )
    user_prompt = f"Language: {req.language}\n{context_block}\nQuestion: {req.question}"
    reply, used_model = call_gemini_with_fallback(system_prompt, user_prompt, json_mode=False)
    return {
        "context_mode": "selected_vacancy" if req.selected_job else ("dataset_context" if req.context else "general_career"),
        "model": used_model,
        "answer": reply,
        "reply": reply,
    }
