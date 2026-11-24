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
    api_key = os.getenv("SCRAPER_API_KEY", "").strip()
    seen_ids: set[str] = set()
    collected_jobs: list[dict] = []

    for kw in KEYWORDS:
        try:
            items = fetch_keyword_jobs
