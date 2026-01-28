import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import re

# ================= הגדרות =================

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "approval_queue.csv"

ROLE_KEYWORDS = [
    "מנהל פרויקטים",
    "Project Manager",
    "PMO",
    "מטמיע",
    "מיישם מערכות",
    "System Implementer"
]

AREA_KEYWORDS = {
    "ירושלים": ["ירושלים"],
    "מרכז": ["תל אביב", "רמת גן", "גבעתיים", "הרצליה", "פתח תקווה", "מרכז"],
    "שפלה": ["ראשון לציון", "רחובות", "נס ציונה", "יבנה", "שפלה"]
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ================= פונקציות עזר =================

def detect_area(text: str):
    for area, keywords in AREA_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return area
    return None


def detect_experience(text: str):
    """
    מחזיר True אם הניסיון מתאים (0–2 שנים)
    False אם מדובר בסניור / 3+ / דרישה גבוהה
    """
    text = text.lower()

    # סינון סניור
    senior_terms = [
        "3+", "4+", "5+", "לפחות 3", "לפחות 4",
        "senior", "ניסיון רב", "ניסיון משמעותי"
    ]
    for term in senior_terms:
        if term in text:
            return False

    # זיהוי ניסיון מתאים
    junior_terms = [
        "ללא ניסיון", "0", "0-1", "1-2", "עד שנתיים",
        "שנה", "שנתיים", "1 שנה", "2 שנים", "junior", "ג'וניור"
    ]
    for term in junior_terms:
        if term in text:
            return True

    # אם לא מצוין ניסיון בכלל – לא לוקחים
    return False


def calculate_score(title: str, text: str):
    score = 0
    title_lower = title.lower()

    # התאמת תפקיד
    for kw in ROLE_KEYWORDS:
        if kw.lower() in title_lower:
            score += 25

    # בוסט ג'וניור
    if "ג'וניור" in title or "junior" in title_lower:
        score += 20

    # בוסט ניסיון 0–2
    if detect_experience(text):
        score += 20

    return score


# ================= AllJobs =================

def fetch_alljobs():
    jobs = []
    url = "https://www.alljobs.co.il/SearchResultsGuest.aspx?position=project"
    res = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    for job in soup.select(".job-card")[:20]:
        title_el = job.select_one(".job-title")
        company_el = job.select_one(".company-name")
        link_el = job.select_one("a")

        if not title_el or not link_el:
            continue

        title = title_el.text.strip()
        full_text = job.text

        # אזור
        area = detect_area(full_text)
        if not area:
            continue

        # ניסיון
        if not detect_experience(full_text):
            continue

        jobs.append({
            "Title": title,
            "Company": company_el.text.strip() if company_el else "לא צוין",
            "Location": area,
            "Score": calculate_score(title, full_text),
            "Link": "https://www.alljobs.co.il" + link_el["href"]
        })

    return jobs


# ================= דרושים =================

def fetch_drushim():
    jobs = []
    url = "https://www.drushim.co.il/jobs/search/מנהל%20פרויקטים"
    res = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    for job in soup.select(".job-item")[:20]:
        title_el = job.select_one(".job-title")
        company_el = job.select_one(".company-name")
        link_el = job.select_one("a")

        if not title_el or not link_el:
            continue

        title = title_el.text.strip()
        full_text = job.text

        # אזור
        area = detect_area(full_text)
        if not area:
            continue

        # ניסיון
        if not detect_experience(full_text):
            continue

        jobs.append({
            "Title": title,
            "Company": company_el.text.strip() if company_el else "לא צוין",
            "Location": area,
            "Score": calculate_score(title, full_text),
            "Link": link_el["href"]
        })

    return jobs


# ================= main =================

def main():
    all_jobs = fetch_alljobs() + fetch_drushim()
    df = pd.DataFrame(all_jobs)

    if df.empty:
        print("❌ לא נמצאו משרות מתאימות (0–2 שנות ניסיון)")
        return

    # בחירת 5 הטובות ביותר
    df = df.sort_values("Score", ascending=False).head(5)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"✅ נשמרו {len(df)} משרות (0–2 שנות ניסיון) ל־{OUTPUT_FILE}")


if __name__ == "__main__":
    main()


