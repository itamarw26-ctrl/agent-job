import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import re

OUTPUT_PATH = Path("output")
OUTPUT_PATH.mkdir(exist_ok=True)

QUEUE_FILE = OUTPUT_PATH / "approval_queue.csv"

KEYWORDS = [
    "מנהל פרויקטים",
    "Project Manager",
    "PMO",
    "מטמיע",
    "מיישם מערכות",
    "System Implementer"
]

def score_job(title: str) -> int:
    score = 0
    for kw in KEYWORDS:
        if kw.lower() in title.lower():
            score += 20
    return score

def fetch_drushim():
    jobs = []
    url = "https://www.drushim.co.il/jobs/search/מנהל%20פרויקטים"
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    for job in soup.select(".job-item")[:10]:
        title = job.select_one(".job-title")
        company = job.select_one(".company-name")
        link = job.select_one("a")

        if not title or not link:
            continue

        jobs.append({
            "Title": title.text.strip(),
            "Company": company.text.strip() if company else "לא צוין",
            "Location": "ישראל",
            "Link": link["href"],
        })
    return jobs

def fetch_alljobs():
    jobs = []
    url = "https://www.alljobs.co.il/SearchResultsGuest.aspx?position=project"
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    for job in soup.select(".job-card")[:10]:
        title = job.select_one(".job-title")
        company = job.select_one(".company-name")
        link = job.select_one("a")

        if not title or not link:
            continue

        jobs.append({
            "Title": title.text.strip(),
            "Company": company.text.strip() if company else "לא צוין",
            "Location": "ישראל",
            "Link": "https://www.alljobs.co.il" + link["href"],
        })
    return jobs

def main():
    jobs = fetch_drushim() + fetch_alljobs()

    df = pd.DataFrame(jobs)
    if df.empty:
        print("No jobs found")
        return

    df["Score"] = df["Title"].apply(score_job)
    df = df.sort_values("Score", ascending=False).head(5)

    df.to_csv(QUEUE_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} jobs to {QUEUE_FILE}")

if __name__ == "__main__":
    main()

