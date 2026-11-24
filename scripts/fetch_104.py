import json
import os
import time
import httpx

KEYWORDS = ["Product Manager 產品經理", "Project Manager 專案經理"]
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.104.com.tw/jobs/search/",
    "Accept": "application/json, text/plain, */*",
}

def main():
    seen_ids = set()
    collected = []

    with httpx.Client(timeout=20.0, headers=HEADERS) as client:
        for kw in KEYWORDS:
            for page in [1, 2]:
                resp = client.get(
                    "https://www.104.com.tw/jobs/search/api/jobs",
                    params={"keyword": kw, "page": page, "pagesize": 20, "order": 15},
                )
                if resp.status_code != 200:
                    print(f"Warning: {kw} page {page} status {resp.status_code}")
                    continue

                items = resp.json().get("data", [])
                for item in items:
                    job_id = str(item.get("jobNo", ""))
                    if not job_id or job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    raw_link = item.get("link", {}).get("job", "")
                    full_url = f"https:{raw_link}" if raw_link.startswith("//") else (raw_link or "https://www.104.com.tw/")

                    collected.append({
                        "job_id": job_id,
                        "source": "104 Job Bank",
                        "source_url": full_url,
                        "job_title_original": item.get("jobName", ""),
                        "company_name_original": item.get("custName", ""),
                        "location": item.get("jobAddrNoDesc", ""),
                        "salary_display": item.get("salaryDesc", "Not provided"),
                        "posting_date": item.get("appearDate", ""),
                        "job_description_original": item.get("description", ""),
                    })
                time.sleep(1.2)

    os.makedirs("data", exist_ok=True)
    with open("data/jobs_104.json", "w", encoding="utf-8") as f:
        json.dump({"total": len(collected), "jobs": collected}, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(collected)} jobs to data/jobs_104.json")

if __name__ == "__main__":
    main()
