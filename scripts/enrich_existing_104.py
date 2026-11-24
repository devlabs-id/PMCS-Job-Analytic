import json
import os
import time
from pathlib import Path
import requests

DATA_PATH = Path("data/jobs_104.json")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

PREFERRED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]


def resolve_gemini_model() -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing in GitHub Secrets!")

    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        res = requests.get(list_url, timeout=30)
        res.raise_for_status()
        models_data = res.json().get("models", [])
        available = []
        for m in models_data:
            name = str(m.get("name", "")).replace("models/", "")
            methods = m.get("supportedGenerationMethods", [])
            if name and "generateContent" in methods:
                available.append(name)

        for pref in PREFERRED_MODELS:
            if pref in available:
                print(f"[INFO] Selected Gemini model: {pref}")
                return pref

        if available:
            print(f"[INFO] Using first available Gemini model: {available[0]}")
            return available[0]
    except Exception as exc:
        print(f"[WARN] Could not list models ({exc}), defaulting to gemini-2.0-flash")

    return "gemini-2.0-flash"


def enrich_chunk(chunk: list[dict], model_name: str) -> dict[str, dict]:
    payload = [
        {
            "job_id": j["job_id"],
            "title": j["job_title_original"],
            "description": j["job_description_original"][:1100],
        }
        for j in chunk
    ]

    prompt = (
        "You are a PM/PjM career analyst. Analyze each 104 Job Bank listing and return ONLY valid JSON "
        "with key 'items' (list). Each item must have:\n"
        "- 'job_id': exact input job_id\n"
        "- 'job_title_en': natural English job title\n"
        "- 'summary_en': 2-3 sentence pure English AI analysis of core JD responsibilities & requirements\n"
        "- 'summary_zh': 2-3 sentence pure Traditional Chinese AI analysis of core JD responsibilities & requirements\n"
        "- 'classification': one of ['PM', 'PjM', 'Hybrid', 'Unclear', 'Other']\n"
        "- 'rationale_en': 1-2 sentence English explanation for the classification\n"
        "- 'rationale_zh': 1-2 sentence Traditional Chinese explanation for the classification\n"
        "- 'competencies': list of 3 to 5 distinct KSA items tailored specifically to this job's actual description, "
        "covering Knowledge, Skills, and Attitudes. Each object must have: "
        "'category' ('Knowledge' | 'Skills' | 'Attitudes'), 'name_en', 'name_zh', "
        "'evidence_type' ('Explicit' | 'Inferred'), and 'excerpt' (exact short quote from original description).\n\n"
        f"Input jobs:\n{json.dumps(payload, ensure_ascii=False)}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"

    for attempt in range(3):
        res = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json",
                },
            },
            timeout=90,
        )
        if res.status_code == 429:
            wait_sec = 15 * (attempt + 1)
            print(f"[429 Rate Limit] Waiting {wait_sec}s before retry {attempt + 1}/3...")
            time.sleep(wait_sec)
            continue
        res.raise_for_status()
        text_out = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text_out)
        items = parsed.get("items", []) if isinstance(parsed, dict) else []
        return {str(x["job_id"]): x for x in items if isinstance(x, dict) and x.get("job_id")}

    raise RuntimeError("Gemini API rate limited after 3 retries.")


def main() -> None:
    model_name = resolve_gemini_model()
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    jobs = raw.get("jobs", [])
    enriched_map: dict[str, dict] = {}

    for i in range(0, len(jobs), 5):
        chunk = jobs[i : i + 5]
        print(f"Analyzing batch {i // 5 + 1} ({len(chunk)} jobs) with {model_name}...")
        enriched_map.update(enrich_chunk(chunk, model_name))
        time.sleep(6)

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
    print(f"Done! Enriched {len(jobs)} jobs using {model_name}.")


if __name__ == "__main__":
    main()
