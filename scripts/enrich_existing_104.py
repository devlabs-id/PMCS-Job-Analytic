import json
import os
import re
import time
from pathlib import Path
import requests

DATA_PATH = Path("data/jobs_104.json")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

OPENROUTER_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "google/gemma-3-27b-it:free",
]

OPENAI_MODELS = [
    "gpt-4o-mini",
]


def extract_json_object(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def call_gemini(prompt: str) -> tuple[dict, str]:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured")
    last_err: Exception | None = None
    for model_name in GEMINI_MODELS:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={GEMINI_API_KEY}"
        )
        try:
            res = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.25,
                        "responseMimeType": "application/json",
                    },
                },
                timeout=60,
            )
            if res.status_code in (404, 429, 503):
                print(f"[Gemini {res.status_code}] '{model_name}' unavailable, skipping...")
                continue
            res.raise_for_status()
            text_out = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            return extract_json_object(text_out), f"gemini:{model_name}"
        except Exception as exc:
            last_err = exc
            print(f"[Gemini WARN] '{model_name}': {exc}")
    raise RuntimeError(f"Gemini exhausted: {last_err}")


def call_openai_compatible(
    provider_label: str,
    endpoint: str,
    api_key: str,
    models: list[str],
    prompt: str,
    extra_headers: dict[str, str] | None = None,
) -> tuple[dict, str]:
    if not api_key:
        raise RuntimeError(f"{provider_label} API key not configured")
    last_err: Exception | None = None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    for model_name in models:
        try:
            payload = {
                "model": model_name,
                "temperature": 0.25,
                "messages": [
                    {
                        "role": "system",
                        "content": "Return ONLY valid JSON matching the requested schema without markdown fences.",
                    },
                    {"role": "user", "content": prompt},
                ],
            }
            if provider_label in ("groq", "openai"):
                payload["response_format"] = {"type": "json_object"}

            res = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            if res.status_code in (401, 402, 404, 429, 503):
                print(f"[{provider_label} {res.status_code}] '{model_name}' unavailable, skipping...")
                continue
            res.raise_for_status()
            text_out = res.json()["choices"][0]["message"]["content"]
            return extract_json_object(text_out), f"{provider_label}:{model_name}"
        except Exception as exc:
            last_err = exc
            print(f"[{provider_label} WARN] '{model_name}': {exc}")
    raise RuntimeError(f"{provider_label} exhausted: {last_err}")


def call_ai_with_multi_provider_fallback(prompt: str) -> tuple[dict, str]:
    providers = [
        ("Primary: Gemini", lambda: call_gemini(prompt)),
        (
            "Fallback 1: Groq",
            lambda: call_openai_compatible(
                "groq",
                "https://api.groq.com/openai/v1/chat/completions",
                GROQ_API_KEY,
                GROQ_MODELS,
                prompt,
            ),
        ),
        (
            "Fallback 2: OpenRouter",
            lambda: call_openai_compatible(
                "openrouter",
                "https://openrouter.ai/api/v1/chat/completions",
                OPENROUTER_API_KEY,
                OPENROUTER_MODELS,
                prompt,
                extra_headers={
                    "HTTP-Referer": "https://devlabs-id.github.io/PMCS-Job-Analytic/",
                    "X-Title": "PMCS-Job-Analytic",
                },
            ),
        ),
        (
            "Fallback 3: OpenAI",
            lambda: call_openai_compatible(
                "openai",
                "https://api.openai.com/v1/chat/completions",
                OPENAI_API_KEY,
                OPENAI_MODELS,
                prompt,
            ),
        ),
    ]

    errors: list[str] = []
    for label, runner in providers:
        try:
            result, used = runner()
            print(f"[OK] Succeeded via {label} ({used})")
            return result, used
        except Exception as exc:
            errors.append(f"{label} -> {exc}")

    raise RuntimeError("All AI providers failed: " + " | ".join(errors))


def build_local_job_fallback(job: dict) -> dict:
    title = str(job.get("job_title_original") or "")
    desc = str(job.get("job_description_original") or "")
    lines = [ln.strip() for ln in desc.splitlines() if ln.strip()]
    snippet_1 = lines[0][:120] if len(lines) > 0 else desc[:120]
    snippet_2 = lines[1][:120] if len(lines) > 1 else desc[120:240]

    is_pm = any(k in (title + desc).lower() for k in ("product", "prd", "roadmap", "產品", "需求分析"))
    classification = "PM" if is_pm else "PjM"

    return {
        "job_id": job["job_id"],
        "job_title_en": job.get("job_title_en") or title,
        "summary_en": f"Role focused on {title}. Key responsibilities include: {snippet_1}",
        "summary_zh": f"此職缺為「{title}」，主要工作內容涵蓋：{snippet_1}",
        "classification": classification,
        "rationale_en": f"Classified as {classification} based on core responsibilities described in {title}.",
        "rationale_zh": f"依據「{title}」之實際工作內容與執行重心判定為 {classification}。",
        "competencies": [
            {
                "category": "Knowledge",
                "name_en": f"Domain Knowledge for {title[:40]}",
                "name_zh": f"{title[:20]} 相關領域知識",
                "evidence_type": "Explicit",
                "excerpt": snippet_1 or desc[:100],
            },
            {
                "category": "Skills",
                "name_en": "Execution & Cross-Functional Coordination",
                "name_zh": "專案執行與跨部門溝通協調",
                "evidence_type": "Explicit",
                "excerpt": snippet_2 or snippet_1 or desc[:100],
            },
            {
                "category": "Attitudes",
                "name_en": "Ownership & Accountability",
                "name_zh": "主動負責與目標導向態度",
                "evidence_type": "Inferred",
                "excerpt": snippet_1 or desc[:100],
            },
        ],
    }


def enrich_chunk(chunk: list[dict]) -> tuple[dict[str, dict], str]:
    payload = [
        {
            "job_id": j["job_id"],
            "title": j["job_title_original"],
            "description": j["job_description_original"][:1100],
        }
        for j in chunk
    ]

    prompt = (
        "You are a PM/PjM career analyst. Analyze each 104 Job Bank listing individually based on its own "
        "title and description, and return ONLY valid JSON with key 'items' (list). Each item must have:\n"
        "- 'job_id': exact input job_id\n"
        "- 'job_title_en': natural English job title\n"
        "- 'summary_en': 2-3 sentence pure English AI analysis specific to this job's JD\n"
        "- 'summary_zh': 2-3 sentence pure Traditional Chinese AI analysis specific to this job's JD\n"
        "- 'classification': one of ['PM', 'PjM', 'Hybrid', 'Unclear', 'Other']\n"
        "- 'rationale_en': 1-2 sentence English explanation for this job's classification\n"
        "- 'rationale_zh': 1-2 sentence Traditional Chinese explanation for this job's classification\n"
        "- 'competencies': list of 3 to 5 distinct KSA items tailored specifically to THIS job's actual description "
        "(never reuse identical generic competencies across different jobs), covering Knowledge, Skills, and Attitudes. "
        "Each object must have: 'category' ('Knowledge' | 'Skills' | 'Attitudes'), 'name_en', 'name_zh', "
        "'evidence_type' ('Explicit' | 'Inferred'), and 'excerpt' (exact short quote from this job's description).\n\n"
        f"Input jobs:\n{json.dumps(payload, ensure_ascii=False)}"
    )

    try:
        parsed, used_model = call_ai_with_multi_provider_fallback(prompt)
        items = parsed.get("items", []) if isinstance(parsed, dict) else []
        mapped = {str(x["job_id"]): x for x in items if isinstance(x, dict) and x.get("job_id")}
        return mapped, used_model
    except Exception as exc:
        print(f"[FALLBACK] All remote AI providers unavailable ({exc}); using per-job local extraction.")
        mapped = {str(j["job_id"]): build_local_job_fallback(j) for j in chunk}
        return mapped, "local-jd-extractor"


def main() -> None:
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    jobs = raw.get("jobs", [])
    enriched_map: dict[str, dict] = {}
    used_engines: set[str] = set()

    for i in range(0, len(jobs), 5):
        chunk = jobs[i : i + 5]
        print(f"Analyzing batch {i // 5 + 1} ({len(chunk)} jobs)...")
        batch_map, engine = enrich_chunk(chunk)
        enriched_map.update(batch_map)
        used_engines.add(engine)
        time.sleep(3)

    for j in jobs:
        ai = enriched_map.get(str(j["job_id"])) or build_local_job_fallback(j)
        j["job_title_en"] = ai.get("job_title_en") or j["job_title_original"]
        j["summary_en"] = ai.get("summary_en") or j["job_description_original"][:240]
        j["summary_zh"] = ai.get("summary_zh") or j["job_description_original"][:240]
        j["classification"] = ai.get("classification") or "PjM"
        j["rationale_en"] = ai.get("rationale_en") or ""
        j["rationale_zh"] = ai.get("rationale_zh") or ""
        comps = ai.get("competencies")
        if isinstance(comps, list) and len(comps) > 0:
            j["competencies"] = comps

    DATA_PATH.write_text(
        json.dumps(
            {
                "total": len(jobs),
                "synced_at": raw.get("synced_at"),
                "jobs": jobs,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Done! Enriched {len(jobs)} jobs using engines: {sorted(used_engines)}")


if __name__ == "__main__":
    main()
