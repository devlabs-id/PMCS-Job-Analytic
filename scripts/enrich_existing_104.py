import json
import os
import time
from pathlib import Path
import requests

DATA_PATH = Path("data/jobs_104.json")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()


def fallback_item(j: dict) -> dict:
    title_zh = j["job_title_original"]
    desc = j["job_description_original"]
    is_pm = ("產品" in title_zh) or ("Product" in title_zh)
    cat = "PM" if is_pm else "PjM"
    return {
        "job_title_en": title_zh,
        "summary_en": (
            f"Role focused on {'product strategy, roadmap, and stakeholder alignment' if is_pm else 'project timeline, milestone tracking, and cross-team coordination'} "
            f"based on the 104 listing: {desc[:180].strip()}"
        ),
        "summary_zh": (
            f"此職缺著重於{'產品規劃、路線圖與需求整合' if is_pm else '專案時程控管、里程碑追蹤與跨部門協調'}，"
            f"依據 104 職缺內容摘要：{desc[:180].strip()}"
        ),
        "classification": cat,
        "rationale_en": f"Classified as {cat} from job title and core responsibilities.",
        "rationale_zh": f"依職稱與核心工作職責歸類為 {cat}。",
        "competencies": [
            {
                "category": "Knowledge",
                "name_en": "Product & Project Lifecycle Domain",
                "name_zh": "產品與專案生命週期領域知識",
                "evidence_type": "Explicit",
                "excerpt": desc[:90].strip(),
            },
            {
                "category": "Skills",
                "name_en": "Cross-Functional Coordination & Tracking",
                "name_zh": "跨部門協調與進度追蹤能力",
                "evidence_type": "Explicit",
                "excerpt": desc[:90].strip(),
            },
            {
                "category": "Attitudes",
                "name_en": "Proactive Problem Solving & Ownership",
                "name_zh": "主動解決問題與當責態度",
                "evidence_type": "Inferred",
                "excerpt": desc[:90].strip(),
            },
        ],
    }


def enrich_chunk(chunk: list[dict]) -> dict[str, dict]:
    if not OPENAI_API_KEY:
        return {str(j["job_id"]): fallback_item(j) for j in chunk}

    payload = [
        {
            "job_id": j["job_id"],
            "title": j["job_title_original"],
            "description": j["job_description_original"][:900],
        }
        for j in chunk
    ]

    for attempt in range(3):
        try:
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
                                "'summary_en': '2-3 sentence pure English AI analysis of JD responsibilities and requirements', "
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
                                "Strictly separate Knowledge, Skills, and Attitudes tailored specifically to each job's actual description."
                            ),
                        },
                        {"role": "user", "content": json.dumps({"items": payload}, ensure_ascii=False)},
                    ],
                },
                timeout=90,
            )
            if res.status_code == 429:
                wait_sec = 12 * (attempt + 1)
                print(f"[429 Rate/Quota Limit] Waiting {wait_sec}s before retry {attempt + 1}/3...")
                time.sleep(wait_sec)
                continue
            res.raise_for_status()
            items = json.loads(res.json()["choices"][0]["message"]["content"]).get("items", [])
            return {str(x["job_id"]): x for x in items if isinstance(x, dict) and x.get("job_id")}
        except Exception as exc:
            print(f"[WARN] Attempt {attempt + 1} error: {exc}")
            time.sleep(5)

    print("[WARN] Falling back to structured extraction for this batch.")
    return {str(j["job_id"]): fallback_item(j) for j in chunk}


def main() -> None:
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    jobs = raw.get("jobs", [])
    enriched_map: dict[str, dict] = {}

    for i in range(0, len(jobs), 3):
        chunk = jobs[i : i + 3]
        print(f"Analyzing batch {i // 3 + 1} ({len(chunk)} jobs)...")
        enriched_map.update(enrich_chunk(chunk))
        time.sleep(8)

    for j in jobs:
        fb = fallback_item(j)
        ai = enriched_map.get(str(j["job_id"]), {})
        j["job_title_en"] = ai.get("job_title_en") or fb["job_title_en"]
        j["summary_en"] = ai.get("summary_en") or fb["summary_en"]
        j["summary_zh"] = ai.get("summary_zh") or fb["summary_zh"]
        j["classification"] = ai.get("classification") or fb["classification"]
        j["rationale_en"] = ai.get("rationale_en") or fb["rationale_en"]
        j["rationale_zh"] = ai.get("rationale_zh") or fb["rationale_zh"]
        comps = ai.get("competencies")
        j["competencies"] = comps if isinstance(comps, list) and len(comps) > 0 else fb["competencies"]

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
    print(f"Done! Updated {len(jobs)} jobs in {DATA_PATH}")


if __name__ == "__main__":
    main()
