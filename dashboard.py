import streamlit as st
import pandas as pd
from pathlib import Path

# ================= נתיבים =================

QUEUE_PATH = Path("output/approval_queue.csv")
DECISIONS_PATH = Path("output/decisions.csv")

# ================= הגדרות עמוד =================

st.set_page_config(
    page_title="Job Approval Dashboard",
    layout="wide"
)

st.title("📋 דשבורד משרות – סוכן חכם")
st.caption("משרות מנהל פרויקטים / PMO / מטמיע מערכות | ניסיון 0–2 | ירושלים / מרכז / שפלה")

# ================= בדיקות בסיס =================

if not QUEUE_PATH.exists():
    st.error("❌ לא נמצא קובץ משרות. ודא שהסוכן רץ בהצלחה.")
    st.stop()

jobs = pd.read_csv(QUEUE_PATH)

if jobs.empty:
    st.success("🎉 אין משרות חדשות להצגה")
    st.stop()

# ================= טעינת החלטות קודמות =================

if DECISIONS_PATH.exists():
    decisions = pd.read_csv(DECISIONS_PATH)
else:
    decisions = pd.DataFrame(columns=["Title", "Company", "Decision"])

# ================= סינון משרות שכבר טופלו =================

jobs = jobs.merge(
    decisions,
    on=["Title", "Company"],
    how="left"
)

jobs = jobs[jobs["Decision"].isna()]

if jobs.empty:
    st.success("🎉 כל המשרות כבר טופלו")
    st.stop()

# ================= הצגת משרות =================

for idx, job in jobs.iterrows():
    with st.container(border=True):
        col_main, col_score, col_actions = st.columns([5, 1.5, 1.5])

        with col_main:
            st.subheader(job["Title"])
            st.write(f"🏢 **חברה:** {job['Company']}")
            st.write(f"📍 **אזור:** {job['Location']}")
            st.markdown(f"🔗 [קישור למשרה]({job['Link']})")

        with col_score:
            st.metric("Score", int(job["Score"]))

        with col_actions:
            if st.button("✅ אשר", key=f"approve_{idx}"):
                decisions.loc[len(decisions)] = [
                    job["Title"],
                    job["Company"],
                    "Approved"
                ]
                decisions.to_csv(DECISIONS_PATH, index=False)
                st.rerun()

            if st.button("❌ דלג", key=f"reject_{idx}"):
                decisions.loc[len(decisions)] = [
                    job["Title"],
                    job["Company"],
                    "Rejected"
                ]
                decisions.to_csv(DECISIONS_PATH, index=False)
                st.rerun()



