import json
import os
import time
from pathlib import Path
import requests

DATA_PATH = Path("data/jobs_104.json")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

BLOCKED_MODEL_KEYWORDS = (
    "image",
    "nano-banana",
    "imagen",
    "veo",
    "tts",
    "audio",
    "embedding",
    "gemma",
    "aqa",
    "robotics",
    "computer-use",
)


def is_text_gemini_model(model_name: str) -> bool:
    lower = model_name.lower()
    if not lower.startswith("gemini-"):
        return False
    return not any(bad in lower for bad in BLOCKED_MODEL_KEYWORDS)


def discover_models() -> list[str]:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing in GitHub Secrets!")

    ordered: list[str] = []
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        res = requests.get(list_url, timeout=30)
        res.raise_for_status()
        available: list[str] = []
        for m in res.json().get("models", []):
            name = str(m.get("name", "")).replace("models/", "")
            methods = m.get("supportedGenerationMethods", [])
            if name and "generateContent" in methods and is_text_gemini_model(name):
                available.append(name)

        for c in CANDIDATE_MODELS:
            if c in available and c not in ordered:
                ordered.append(c)
        for name in available:
            if name not in ordered and ("flash" in name.lower() or "pro" in name.lower()):
                ordered.append(name)
    except Exception as exc:
        print(f"[WARN] ListModels failed ({exc}); using default text candidates.")

    for c in CANDIDATE_MODELS:
        if c not in ordered:
            ordered.append(c)

    return ordered[:8]


def call_gemini_with_model_fallback(prompt: str, models: list[str]) -> tuple[dict, str]:
    last_error: Exception | None = None

    for model_name in models:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={GEMINI_API_KEY}"
        )
        for attempt in range(2):
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
                    timeout=90,
                )
                if res.status_code == 404:
                    print(f"[404] Model '{model_name}' not found; switching model...")
                    break
                if res.status_code == 429:
                    wait_sec = 5 * (attempt + 1)
                    print(f"[429 Rate Limit] Model '{model_name}' waiting {wait_sec}s (retry {attempt + 1}/2)...")
                    time.sleep(wait_sec)
                    continue
                res.raise_for_status()
                text_out = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text_out), model_name
            except Exception as exc:
                last_error = exc
                print(f"[WARN] Error on '{model_name}' attempt {attempt + 1}/2: {exc}")
                time.sleep(3)

    raise RuntimeError(f"All Gemini text models failed. Last error: {last_error}")


def enrich_chunk(chunk: list[dict], models: list[str]) -> tuple[dict[str, dict], str]:
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
        "(do not reuse generic competencies across different jobs), covering Knowledge, Skills, and Attitudes. "
        "Each object must have: 'category' ('Knowledge' | 'Skills' | 'Attitudes'), 'name_en', 'name_zh', "
        "'evidence_type' ('Explicit' | 'Inferred'), and 'excerpt' (exact short quote from this job's description).\n\n"
        f"Input jobs:\n{json.dumps(payload, ensure_ascii=False)}"
    )

    parsed, used_model = call_gemini_with_model_fallback(prompt, models)
    items = parsed.get("items", []) if isinstance(parsed, dict) else []
    mapped = {str(x["job_id"]): x for x in items if isinstance(x, dict) and x.get("job_id")}
    return mapped, used_model


def main() -> None:
    models = discover_models()
    print(f"[INFO] Filtered text candidate models: {models}")

    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    jobs = raw.get("jobs", [])
    enriched_map: dict[str, dict] = {}
    active_model = models[0]

    for i in range(0, len(jobs), 5):
        chunk = jobs[i : i + 5]
        print(f"Analyzing batch {i // 5 + 1} ({len(chunk)} jobs)...")
        batch_map, active_model = enrich_chunk(chunk, models)
        enriched_map.update(batch_map)
        time.sleep(5)

    for j in jobs:
        ai = enriched_map.get(str(j["job_id"]))
        if not ai:
            continue
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
    print(f"Done! Enriched {len(jobs)} jobs using {active_model}.")


if __name__ == "__main__":
    main()
