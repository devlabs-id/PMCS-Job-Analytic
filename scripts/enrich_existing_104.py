import json
import os
from pathlib import Path
import requests

DATA_PATH = Path("data/jobs_104.json")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()


def enrich_chunk(chunk: list[dict]) -> dict[str, dict]:
    payload = [
        {
            "job_id": j["job_id"],
            "title": j["job_title_original"],
            "description": j["job_description_original"][:1200],
        }
        for j in chunk
    ]
    res = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Analyze each 104 Job Bank listing for PM/PjM roles and return JSON: "
                        "{'items': [ { 'job_id': str, 'job_title_en': str, "
                        "'summary_en': '2-3 sentence English AI analysis of JD responsibilities and requirements', "
                        "'summary_zh': '2-3句繁體中文 AI 工作職責與需求重點解析', "
                        "'classification': 'PM' | 'PjM' | 'Hybrid' | 'Unclear' | 'Other', "
                        "'rationale_en': '1-2 sentence English classification rationale', "
                        "'rationale_zh': '1-2句繁體中文分類依據說明', "
                        "'competencies': [ "
                        "{ 'category': 'Knowledge' | 'Skills' | 'Attitudes', "
                        "'name_en': str, 'name_zh': str, "
                        "'evidence_type': 'Explicit' | 'Inferred', "
                        "'excerpt': 'short exact quote from original description' } "
                        "] } ]}. "
                        "Ensure 'competencies' strictly separates Knowledge, Skills, and Attitudes based on the job requirements."
                    ),
                },
                {"role": "user", "content": json.dumps({"items": payload}, ensure_ascii=False)},
            ],
        },
        timeout=90,
    )
    res.raise_for_status()
    items = json.loads(res.json()["choices"][0]["message"]["content"]).get("items", [])
    return {str(x["job_id"]): x for x in items if isinstance(x, dict) and x.get("job_id")}


def main() -> None:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing in GitHub Secrets!")

    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    jobs = raw.get("jobs", [])
    enriched_map: dict[str, dict] = {}

    for i in range(0, len(jobs), 6):
        chunk = jobs[i : i + 6]
        print(f"Analyzing batch {i // 6 + 1} ({len(chunk)} jobs)...")
        enriched_map.update(enrich_chunk(chunk))

    for j in jobs:
        ai = enriched_map.get(str(j["job_id"]), {})
        j["job_title_en"] = ai.get("job_title_en") or j["job_title_original"]
        j["summary_en"] = ai.get("summary_en") or j["job_description_original"][:240]
        j["summary_zh"] = ai.get("summary_zh") or j["job_description_original"][:240]
        j["classification"] = ai.get("classification") or "PjM"
        j["rationale_en"] = ai.get("rationale_en") or ""
        j["rationale_zh"] = ai.get("rationale_zh") or ""
        j["competencies"] = ai.get("competencies") or []

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
    print(f"Done! Enriched {len(jobs)} jobs in {DATA_PATH}")


if __name__ == "__main__":
    main()
