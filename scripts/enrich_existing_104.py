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


def extract_json_payload(raw_text: str):
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
        if match:
            return json.loads(match.group(1))
        raise


def discover_gemini_models() -> list[str]:
    if not GEMINI_API_KEY:
        return []
    try:
        r = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}",
            timeout=20,
        )
        if r.status_code != 200:
            print(f"[Gemini discovery {r.status_code}] {r.text[:160]}")
            return ["gemini-2.0-flash", "gemini-1.5-flash"]
        models = []
        for m in r.json().get("models", []):
            name = m.get("name", "").replace("models/", "")
            methods = m.get("supportedGenerationMethods", [])
            if "generateContent" in methods and "gemini" in name and "embedding" not in name and "vision" not in name:
                models.append(name)
        # Prioritaskan flash
        models.sort(key=lambda x: (0 if "flash" in x else 1, x))
        return models[:5] if models else ["gemini-2.0-flash", "gemini-1.5-flash"]
    except Exception as exc:
        print(f"[Gemini discovery WARN] {exc}")
        return ["gemini-2.0-flash", "gemini-1.5-flash"]


def discover_groq_models() -> list[str]:
    if not GROQ_API_KEY:
        return []
    try:
        r = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            timeout=20,
        )
        if r.status_code != 200:
            print(f"[Groq discovery {r.status_code}] {r.text[:160]}")
            return []
        models = [
            m["id"]
            for m in r.json().get("data", [])
            if isinstance(m, dict)
            and m.get("id")
            and not any(bad in m["id"].lower() for bad in ("whisper", "guard", "tts", "embed"))
        ]
        models.sort(key=lambda x: (0 if "70b" in x else (1 if "llama" in x else 2), x))
        return models[:4]
    except Exception as exc:
        print(f"[Groq discovery WARN] {exc}")
        return []


def discover_openrouter_free_models() -> list[str]:
    if not OPENROUTER_API_KEY:
        return []
    try:
        r = requests.get("https://openrouter.ai/api/v1/models", timeout=20)
        if r.status_code != 200:
            return []
        free_models = []
        for m in r.json().get("data", []):
            mid = m.get("id", "")
            pricing = m.get("pricing", {})
            if mid.endswith(":free") or (str(pricing.get("prompt")) == "0" and str(pricing.get("completion")) == "0"):
                if not any(bad in mid.lower() for bad in ("vision", "vl", "embed", "audio")):
                    free_models.append(mid)
        free_models.sort(key=lambda x: (0 if any(k in x.lower() for k in ("llama", "qwen", "gemini", "mistral")) else 1, x))
        return free_models[:5]
    except Exception as exc:
        print(f"[OpenRouter discovery WARN] {exc}")
        return []


def call_gemini(prompt: str, models: list[str]):
    if not GEMINI_API_KEY or not models:
        raise RuntimeError("Gemini unavailable")
    last_err: Exception | None = None
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            res = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.25, "responseMimeType": "application/json"},
                },
                timeout=60,
            )
            if res.status_code != 200:
                print(f"[Gemini {res.status_code}] '{model_name}': {res.text[:140]}")
                last_err = RuntimeError(f"HTTP {res.status_code}")
                continue
            text_out = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            return extract_json_payload(text_out), f"gemini:{model_name}"
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
):
    if not api_key or not models:
        raise RuntimeError(f"{provider_label} unavailable")
    last_err: Exception | None = None
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)

    for model_name in models:
        try:
            payload = {
                "model": model_name,
                "temperature": 0.25,
                "messages": [
                    {"role": "system", "content": "Return ONLY valid JSON matching the requested schema without markdown fences."},
                    {"role": "user", "content": prompt},
                ],
            }
            if provider_label in ("groq", "openai"):
                payload["response_format"] = {"type": "json_object"}

            res = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            if res.status_code != 200:
                print(f"[{provider_label} {res.status_code}] '{model_name}': {res.text[:140]}")
                last_err = RuntimeError(f"HTTP {res.status_code}")
                continue
            text_out = res.json()["choices"][0]["message"]["content"]
            return extract_json_payload(text_out), f"{provider_label}:{model_name}"
        except Exception as exc:
            last_err = exc
            print(f"[{provider_label} WARN] '{model_name}': {exc}")
    raise RuntimeError(f"{provider_label} exhausted: {last_err}")


def build_local_job_fallback(job: dict) -> dict:
    title = str(job.get("job_title_original") or "")
    desc = str(job.get("job_description_original") or "")
    lines = [ln.strip() for ln in desc.splitlines() if ln.strip()]
    snippet_1 = lines[0][:100] if len(lines) > 0 else desc[:100]
    snippet_2 = lines[1][:100] if len(lines) > 1 else snippet_1
    is_pm = any(k in f"{title} {desc}".lower() for k in ("product", "prd", "roadmap", "產品", "需求分析", "企劃"))
    classification = "PM" if is_pm else "PjM"
    return {
        "job_id": job["job_id"],
        "job_title_en": job.get("job_title_en") or title,
        "summary_en": f"This {classification} role at {job.get('company_name_original', 'the company')} focuses on {title}.",
        "summary_zh": f"此職缺為「{title}」，主要工作內容涵蓋：{snippet_1}",
        "classification": classification,
        "rationale_en": f"Classified as {classification} based on responsibilities in {title}.",
        "rationale_zh": f"依據「{title}」之實際工作內容判定為 {classification}。",
        "competencies": [
            {"category": "Knowledge", "name_en": "Domain & Product/Project Knowledge", "name_zh": "領域與產品專案知識", "evidence_type": "Explicit", "excerpt": snippet_1 or desc[:100]},
            {"category": "Skills", "name_en": "Cross-Functional Execution & Coordination", "name_zh": "跨部門協作與執行控管", "evidence_type": "Explicit", "excerpt": snippet_2 or desc[:100]},
            {"category": "Attitudes", "name_en": "Ownership & Accountability", "name_zh": "主動負責與目標導向", "evidence_type": "Inferred", "excerpt": snippet_1 or desc[:100]},
        ],
    }


def main() -> None:
    gemini_models = discover_gemini_models()
    groq_models = discover_groq_models()
    openrouter_models = discover_openrouter_free_models()
    openai_models = ["gpt-4o-mini"] if OPENAI_API_KEY else []

    print(f"Discovered models -> Gemini: {gemini_models} | Groq: {groq_models} | OpenRouter: {openrouter_models}")

    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    jobs = raw.get("jobs", [])
    enriched_map: dict[str, dict] = {}
    used_engines: set[str] = set()

    for i in range(0, len(jobs), 5):
        chunk = jobs[i : i + 5]
        print(f"Analyzing batch {i // 5 + 1} ({len(chunk)} jobs)...")
        payload = [
            {"job_id": j["job_id"], "title": j["job_title_original"], "description": j["job_description_original"][:1100]}
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

        batch_done = False
        for label, runner in [
            ("Gemini", lambda: call_gemini(prompt, gemini_models)),
            ("Groq", lambda: call_openai_compatible("groq", "https://api.groq.com/openai/v1/chat/completions", GROQ_API_KEY, groq_models, prompt)),
            ("OpenRouter", lambda: call_openai_compatible("openrouter", "https://openrouter.ai/api/v1/chat/completions", OPENROUTER_API_KEY, openrouter_models, prompt, {"HTTP-Referer": "https://devlabs-id.github.io/PMCS-Job-Analytic/", "X-Title": "PMCS-Job-Analytic"})),
            ("OpenAI", lambda: call_openai_compatible("openai", "https://api.openai.com/v1/chat/completions", OPENAI_API_KEY, openai_models, prompt)),
        ]:
            try:
                parsed, used = runner()
                items = parsed if isinstance(parsed, list) else (parsed.get("items") or parsed.get("jobs") or [])
                mapped = {str(x["job_id"]): x for x in items if isinstance(x, dict) and x.get("job_id")}
                if mapped:
                    enriched_map.update(mapped)
                    used_engines.add(used)
                    print(f"[OK] Batch {i // 5 + 1} enriched via {label} ({used})")
                    batch_done = True
                    break
            except Exception as exc:
                print(f"[{label} skip] {exc}")

        if not batch_done:
            for j in chunk:
                enriched_map[str(j["job_id"])] = build_local_job_fallback(j)
            used_engines.add("local-jd-extractor")

        time.sleep(2)

    for j in jobs:
        ai = enriched_map.get(str(j["job_id"])) or build_local_job_fallback(j)
        j["job_title_en"] = ai.get("job_title_en") or j["job_title_original"]
        j["summary_en"] = ai.get("summary_en") or ""
        j["summary_zh"] = ai.get("summary_zh") or ""
        j["classification"] = ai.get("classification") or "PjM"
        j["rationale_en"] = ai.get("rationale_en") or ""
        j["rationale_zh"] = ai.get("rationale_zh") or ""
        comps = ai.get("competencies")
        if isinstance(comps, list) and len(comps) > 0:
            j["competencies"] = comps

    DATA_PATH.write_text(
        json.dumps({"total": len(jobs), "synced_at": raw.get("synced_at"), "jobs": jobs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Done! Enriched {len(jobs)} jobs using engines: {sorted(used_engines)}")


if __name__ == "__main__":
    main()
