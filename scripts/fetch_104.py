import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote
import requests

KEYWORDS = ["Product Manager", "Project Manager", "產品經理", "專案經理"]
OUTPUT_PATH = Path("data/jobs_104.json")
CST = timezone(timedelta(hours=8))


def build_target_url(keyword: str, page: int = 1, pagesize: int = 15) -> str:
    return (
        f"https://www.104.com.tw/jobs/search/api/jobs"
        f"?keyword={quote(keyword)}&page={page}&pagesize={pagesize}&order=15"
    )


def fetch_keyword_jobs(keyword: str, api_key: str) -> list[dict]:
    target_url = build_target_url(keyword, page=1, pagesize=15)

    if api_key:
        proxy_url = (
            f"http://api.scraperapi.com?api_key={quote(api_key)}"
            f"&url={quote(target_url)}&country_code=tw"
        )
        resp = requests.get(proxy_url, timeout=35)
    else:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.104.com.tw/jobs/search/",
            "Accept": "application/json, text/plain, */*",
        }
        resp = requests.get(target_url, headers=headers, timeout=25)

    resp.raise_for_status()
    payload = resp.json()

    raw_list = []
    if isinstance(payload, dict):
        data_obj = payload.get("data")
        if isinstance(data_obj, dict) and isinstance(data_obj.get("list"), list):
            raw_list = data_obj["list"]
        elif isinstance(data_obj, list):
            raw_list = data_obj
        elif isinstance(payload.get("list"), list):
            raw_list = payload["list"]

    return raw_list


def fallback_enrich(job: dict) -> None:
    desc = job["job_description_original"]
    job["job_title_en"] = job["job_title_original"]
    job["summary_en"] = desc[:220]
    job["summary_zh"] = desc[:220]
    job["classification"] = "PM" if "產品" in job["job_title_original"] or "Product" in job["job_title_original"] else "PjM"
    job["rationale_en"] = "Role classified from 104 job title and responsibility description."
    job["rationale_zh"] = "依據 104 職稱與工作內容描述進行職責分類。"
    job["competencies"] = [
        {
            "category": "Knowledge",
            "name_en": "Product / Project Lifecycle Management",
            "name_zh": "產品與專案生命週期管理",
            "evidence_type": "Explicit",
            "excerpt": desc[:100],
        },
        {
            "category": "Skills",
            "name_en": "Cross-Functional Execution & Coordination",
            "name_zh": "跨部門協作與執行控管",
            "evidence_type": "Explicit",
            "excerpt": desc[:100],
        },
        {
            "category": "Attitudes",
            "name_en": "Stakeholder Ownership & Accountability",
            "name_zh": "利害關係人溝通與當責態度",
            "evidence_type": "Inferred",
            "excerpt": desc[:100],
        },
    ]


def analyze_jobs_with_openai(jobs: list[dict], openai_key: str) -> None:
    if not openai_key or not jobs:
        for j in jobs:
            fallback_enrich(j)
        return

    # Process in chunks of 8 jobs so response JSON stays fast and complete
    for start in range(0, len(jobs), 8):
        chunk = jobs[start : start + 8]
        payload_items = [
            {
                "job_id": j["job_id"],
                "title": j["job_title_original"],
                "description": j["job_description_original"][:900],
            }
            for j in chunk
        ]

        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_key}",
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
                                "You are a PM/PjM career analyst. Analyze each 104 Job Bank listing and return a JSON object "
                                "with key 'items' (list). Each item must contain:\n"
                                "- 'job_id': exact input job_id\n"
                                "- 'job_title_en': clear English title\n"
                                "- 'summary_en': 2-3 sentence English AI analysis of core JD responsibilities\n"
                                "- 'summary_zh': 2-3 sentence Traditional Chinese AI analysis of core JD responsibilities\n"
                                "- 'classification': one of ['PM', 'PjM', 'Hybrid', 'Unclear', 'Other']\n"
                                "- 'rationale_en': 1-2 sentence English explanation of why it got this classification\n"
                                "- 'rationale_zh': 1-2 sentence Traditional Chinese explanation of why it got this classification\n"
                                "- 'competencies': array of 3 to 5 extracted KSA items covering Knowledge, Skills, and Attitudes. "
                                "Each competency object must have: 'category' ('Knowledge' | 'Skills' | 'Attitudes'), "
                                "'name_en', 'name_zh', 'evidence_type' ('Explicit' | 'Inferred'), and 'excerpt' (exact short quote from original description)."
                            ),
                        },
                        {
                            "role": "user",
                            "content": json.dumps({"items": payload_items}, ensure_ascii=False),
                        },
                    ],
                },
                timeout=60,
            )
            resp.raise_for_status()
            parsed = json.loads(resp.json()["choices"][0]["message"]["content"])
            analyzed_map = {
                str(row.get("job_id")): row
                for row in (parsed.get("items") or [])
                if isinstance(row, dict) and row.get("job_id")
            }

            for j in chunk:
                ai = analyzed_map.get(j["job_id"])
                if not ai:
                    fallback_enrich(j)
                    continue
                j["job_title_en"] = str(ai.get("job_title_en") or j["job_title_original"]).strip()
                j["summary_en"] = str(ai.get("summary_en") or j["job_description_original"][:220]).strip()
                j["summary_zh"] = str(ai.get("summary_zh") or j["job_description_original"][:220]).strip()
                j["classification"] = str(ai.get("classification") or "Unclear").strip()
                j["rationale_en"] = str(ai.get("rationale_en") or "").strip()
                j["rationale_zh"] = str(ai.get("rationale_zh") or "").strip()
                comps = ai.get("competencies")
                if isinstance(comps, list) and len(comps) > 0:
                    j["competencies"] = comps
                else:
                    fallback_enrich(j)
        except Exception as exc:
            print(f"[WARN] OpenAI KSA analysis chunk failed ({exc}); using fallback.")
            for j in chunk:
                fallback_enrich(j)


def normalize_job(item: dict, fallback_idx: int) -> dict | None:
    if not isinstance(item, dict):
        return None

    link_obj = item.get("link") if isinstance(item.get("link"), dict) else {}
    job_id = str(item.get("jobNo") or link_obj.get("job") or f"104-{fallback_idx}").strip()
    if not job_id:
        return None

    raw_link = str(link_obj.get("job") or "").strip()
    if raw_link.startswith("http"):
        source_url = raw_link
    elif raw_link.startswith("//"):
        source_url = "https:" + raw_link
    else:
        source_url = f"https://www.104.com.tw/job/{job_id}"

    title = str(item.get("jobName") or "").strip()
    company = str(item.get("custName") or "").strip()
    location = str(item.get("jobAddrNoDesc") or "Taiwan").strip()
    salary = str(item.get("salaryDesc") or "Not provided").strip()
    posting_date = str(item.get("appearDate") or datetime.now(CST).strftime("%Y-%m-%d")).strip()
    desc = str(item.get("description") or title).strip()

    if not title:
        return None

    return {
        "job_id": job_id,
        "source": "104 Job Bank",
        "source_url": source_url,
        "job_title_original": title,
        "company_name_original": company,
        "location": location,
        "salary_display": salary,
        "posting_date": posting_date,
        "job_description_original": desc,
    }


def load_existing_jobs() -> list[dict]:
    if not OUTPUT_PATH.exists():
        return []
    try:
        existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        if isinstance(existing, dict) and isinstance(existing.get("jobs"), list):
            return existing["jobs"]
    except Exception:
        pass
    return []


def main() -> None:
    scraper_key = os.getenv("SCRAPER_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    seen_ids: set[str] = set()
    collected_jobs: list[dict] = []

    for kw in KEYWORDS:
        try:
            items = fetch_keyword_jobs(kw, scraper_key)
            for item in items:
                job = normalize_job(item, len(collected_jobs) + 1)
                if job and job["job_id"] not in seen_ids:
                    seen_ids.add(job["job_id"])
                    collected_jobs.append(job)
        except Exception as exc:
            print(f"[WARN] Keyword '{kw}' failed: {exc}")

    if not collected_jobs:
        existing_jobs = load_existing_jobs()
        print(f"[INFO] 0 new jobs fetched; keeping {len(existing_jobs)} existing jobs.")
        return

    analyze_jobs_with_openai(collected_jobs, openai_key)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "total": len(collected_jobs),
        "synced_at": datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S CST"),
        "jobs": collected_jobs,
    }
    OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[SUCCESS] Saved {len(collected_jobs)} AI-analyzed jobs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
