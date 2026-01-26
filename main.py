import json
import csv
from pathlib import Path

# ---------- שלב 1: טעינת פרופיל ----------
with open("config/profile.json", encoding="utf-8") as f:
    profile = json.load(f)

MIN_SCORE = profile["min_score"]

# ---------- שלב 2: משרות לדוגמה ----------
jobs = [
    {
        "title": "PMO Analyst – BI Projects",
        "company": "TechCorp",
        "location": "מרכז",
        "description": "Junior PMO role with KPI reporting, Power BI dashboards and Excel work",
        "url": "https://example.com/job1"
    },
    {
        "title": "Project Manager",
        "company": "BuildIt",
        "location": "צפון",
        "description": "Senior project manager with 5+ years experience required",
        "url": "https://example.com/job2"
    },
    {
        "title": "System Implementer (Junior)",
        "company": "DataSystems",
        "location": "ירושלים",
        "description": "Implementation of BI systems, QLIK, SQL and user training",
        "url": "https://example.com/job3"
    }
]

# ---------- שלב 3: חישוב ציון ----------
def calculate_score(job, profile):
    score = 0
    text = (job["title"] + " " + job["description"]).lower()

    # רמת ניסיון – 40%
    if "junior" in text or "entry" in text or "1-2" in text:
        score += 40

    # מילות מפתח – 40%
    keyword_hits = sum(1 for skill in profile["skills"] if skill.lower() in text)
    score += min(keyword_hits * 10, 40)

    # כותרת – 10%
    if any(role.lower() in job["title"].lower() for role in profile["roles"]):
        score += 10

    # מיקום – 10%
    if job["location"] in profile["locations"]:
        score += 10

    return score

# ---------- שלב 4: סינון ----------
approved_jobs = []

for job in jobs:
    score = calculate_score(job, profile)

    # מילות פסילה
    if any(word.lower() in job["description"].lower() for word in profile["exclude"]):
        continue

    if score >= MIN_SCORE:
        job["score"] = score
        approved_jobs.append(job)

# ---------- שלב 5: יצירת CSV ----------
output_path = Path("output/approval_queue.csv")

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Company", "Location", "Score", "Link"])

    for job in approved_jobs:
        writer.writerow([
            job["title"],
            job["company"],
            job["location"],
            job["score"],
            job["url"]
        ])

print(f"✔ נוצר קובץ: {output_path}")


