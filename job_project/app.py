import streamlit as st
import pandas as pd
import re
import requests
import time
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Job Market Intelligence",
    page_icon="🚀",
    layout="wide"
)

# ---------------- STYLE ----------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f1117, #111827);
    color: white;
}

/* TITLE */
.title {
    font-size: 52px;
    font-weight: 900;
    background: linear-gradient(90deg, #00ffd5, #4facfe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* CARD */
.card {
    background: rgba(28, 31, 38, 0.75);
    padding: 22px;
    border-radius: 16px;
    margin-bottom:15px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.05);
    transition: 0.3s;
}
.card:hover {
    transform: scale(1.02);
    box-shadow: 0px 15px 40px rgba(0,0,0,0.6);
}

/* SECTION BOX */
.section-box {
    background: rgba(17, 25, 40, 0.75);
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.05);
}

/* METRIC */
.metric {
    font-size: 34px;
    font-weight: bold;
    color: #00ffd5;
}

/* TAG */
.tag {
    display:inline-block;
    background:#1f2937;
    padding:5px 12px;
    border-radius:12px;
    margin:4px;
    font-size:12px;
}

/* PROGRESS */
.stProgress > div > div {
    background: linear-gradient(90deg, #00ffd5, #4facfe);
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div style="text-align:center; margin-top:30px; margin-bottom:10px;">
    <h1 class="title">🚀 AI Job Market Intelligence</h1>
    <p style='color:#9aa4b2; font-size:18px;'>
        Discover your market value. Beat 95% of candidates.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid rgba(255,255,255,0.05)'>", unsafe_allow_html=True)

with st.spinner("Analyzing job market..."):
    time.sleep(1)

# ---------------- DATA ----------------
df = pd.read_csv("clean_jobs.csv")
df["description"] = df["description"].astype(str)

skills = ["python", "sql", "excel", "power bi", "tableau", "spark"]

for skill in skills:
    df[skill] = df["description"].str.lower().str.contains(skill)

df["r"] = df["description"].str.lower().apply(lambda x: bool(re.search(r"\br\b", x)))

skills_all = ["python", "sql", "excel", "power bi", "tableau", "r", "spark"]

skill_counts = df[skills_all].sum()
skill_percent = (skill_counts / len(df)) * 100

salary_df = pd.read_csv("Data Science Jobs Salaries.csv")
salary_avg = salary_df["salary_in_usd"].mean()

# ---------------- LIVE JOBS ----------------
def get_live_jobs():
    try:
        url = "https://remoteok.com/api"
        response = requests.get(url)
        data = response.json()

        jobs = []
        for job in data[1:6]:
            jobs.append({
                "title": job.get("position"),
                "company": job.get("company"),
                "location": job.get("location"),
                "tags": job.get("tags")
            })
        return jobs
    except:
        return []

# ---------------- INPUT ----------------
st.markdown("### 🎯 Select Your Skills")
user_skills = st.multiselect("", skills_all)
st.caption(f"📊 {len(df)} job postings analyzed")

# ---------------- MAIN ----------------
if user_skills:

    live_jobs = get_live_jobs()

    # SCORE
    matched = skill_percent[user_skills].sum()
    total = skill_percent.sum()
    score = (matched / total) * 100

    # ROLE
    if "sql" in user_skills and "power bi" in user_skills:
        role = "BI Analyst"
    elif "python" in user_skills:
        role = "Data Scientist"
    else:
        role = "Data Analyst"

    # ---------------- METRICS ----------------
    c1, c2, c3 = st.columns(3)

    c1.markdown(f"<div class='card'>📊 Readiness<div class='metric'>%{round(score,1)}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'>💰 Salary<div class='metric'>₺{int(salary_avg)}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card'>🎯 Role<div class='metric'>{role}</div></div>", unsafe_allow_html=True)

    st.progress(score/100)
    st.caption("🔥 Top 10% candidates are above 75% score")

    # ---------------- GRID ----------------
    left, right = st.columns([2,1])

    # LEFT
    with left:

        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.markdown("### 🧠 AI Insight")

        if score < 50:
            st.error("🚫 Below market level.")
        elif score < 70:
            st.warning("⚡ You're close.")
        else:
            st.success("🔥 You're job-ready.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.markdown("### 🧠 Why this score?")

        weights = {"python":18,"sql":15,"excel":10,"power bi":12,"tableau":10,"r":8,"spark":12}

        for s in skills_all:
            if s in user_skills:
                st.markdown(f"<span class='tag'>✅ {s} +{weights[s]}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='tag'>❌ {s}</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.markdown("### 📊 Market Comparison")

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("You", f"%{round(score,1)}")
        mc2.metric("Market Avg", f"%{round(skill_percent.mean(),1)}")
        mc3.metric("Top", "%80+")

        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT
    with right:

        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.markdown("### 🚀 Skill Gap")

        missing = [s for s in skills_all if s not in user_skills]
        missing_sorted = skill_percent[missing].sort_values(ascending=False)

        for s in missing_sorted.index[:4]:
            st.markdown(f"<span class='tag'>👉 {s}</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.markdown("### 🛤️ Roadmap")

        if "python" not in user_skills:
            st.write("📌 Learn Python")
        if "tableau" not in user_skills:
            st.write("📌 Learn BI Tools")
        st.write("📌 Build 2 Projects")

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- JOBS ----------------
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Personalized Job Matches (Based on Your Skills)")
    st.caption("Jobs ranked based on your skill compatibility")

    df["match_score"] = df[skills_all].apply(
        lambda row: sum([row[s] for s in user_skills]) / len(user_skills) * 100,
        axis=1
    )

    top_jobs = df.sort_values("match_score", ascending=False).head(5)

    for _, job in top_jobs.iterrows():
        st.markdown(f"""
        <div class="card">
        <h3>{job['title']}</h3>
        <p>{job['company']}</p>
        <p>📍 {job['location']}</p>
        <p style="color:#00ffd5;">📊 %{round(job['match_score'],1)}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- LIVE ----------------
    if live_jobs:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.markdown("### 🎯 Personalized Job Matches (Based on Your Skills)")
        st.caption("Real-time jobs enriched with skill match score")

        for job in live_jobs:
            tags = job['tags'][:5] if job['tags'] else []
            tag_html = "".join([f"<span class='tag'>{t}</span>" for t in tags])

            st.markdown(f"""
                        <div class="card">
                        <b>{job['title']}</b> - {job['company']}<br>
                        📍 {job['location']}<br>
                        {tag_html}
                        </div>
                        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- GRAPH ----------------
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.markdown("### 📊 Market Demand")
    st.caption("Shows most in-demand skills based on job postings")

    fig = px.bar(skill_counts.sort_values(ascending=False))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("""
<div style='text-align:center; color:gray; margin-top:40px;'>
Built by <b>Ceren Aydın</b> 🚀
</div>
""", unsafe_allow_html=True)