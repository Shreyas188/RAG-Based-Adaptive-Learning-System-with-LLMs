"""
frontend/pages/5_Dashboard.py — Clean light dashboard
"""
import streamlit as st
import httpx
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Dashboard · RAG Tutor", page_icon="📊", layout="wide")
css = Path(__file__).parent.parent / "assets" / "style.css"
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

for k, v in {"backend_url": "http://localhost:8000", "session_id": "session_001"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

BACKEND = st.session_state.backend_url
SID     = st.session_state.session_id

st.markdown("""
<div class="page-header">
    <div class="page-title">📊 Learning Dashboard</div>
    <div class="page-subtitle">Track your progress and get personalised recommendations</div>
</div>
""", unsafe_allow_html=True)

# Refresh
if st.button("🔄 Refresh", use_container_width=False):
    st.cache_data.clear()

# ── Fetch data ────────────────────────────────────────────────
@st.cache_data(ttl=20)
def get_data(sid, backend):
    try:
        analytics   = httpx.get(f"{backend}/api/analytics/{sid}", timeout=8).json()
        quiz_scores = httpx.get(f"{backend}/api/analytics/quiz-scores/{sid}", timeout=8).json().get("scores", [])
        return analytics, quiz_scores
    except Exception:
        return None, []

analytics, quiz_scores = get_data(SID, BACKEND)

# ── Metrics ───────────────────────────────────────────────────
if analytics:
    st.markdown("#### Your Learning Stats")
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    avg = analytics.get("avg_quiz_score", 0)
    score_color = "#16A34A" if avg >= 70 else "#D97706" if avg >= 40 else "#DC2626"

    for col, icon, val, label in [
        (c1, "💬", analytics.get("total_queries",0),      "Questions Asked"),
        (c2, "📝", analytics.get("total_quiz_attempts",0), "Quiz Attempts"),
        (c3, "🎯", f"{avg:.0f}%",                         "Avg Quiz Score"),
        (c4, "📚", analytics.get("most_queried_chapter","N/A")[:16], "Top Chapter"),
    ]:
        col.markdown(
            f'<div class="metric-card">'
            f'<div style="font-size:1.6rem;">{icon}</div>'
            f'<div class="metric-value">{val}</div>'
            f'<div class="metric-label">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("<br>", unsafe_allow_html=True)

# ── Quiz Chart ────────────────────────────────────────────────
if quiz_scores:
    st.markdown("#### Quiz Performance")
    df = pd.DataFrame(quiz_scores)

    colors = ["#16A34A" if p >= 70 else "#D97706" if p >= 40 else "#DC2626"
              for p in df["percentage"]]

    fig = go.Figure(go.Bar(
        x=[f"Quiz {i+1}" for i in range(len(df))],
        y=df["percentage"],
        marker_color=colors,
        text=[f"{p:.0f}%" for p in df["percentage"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Score: %{y:.0f}%<extra></extra>",
    ))
    fig.add_hline(y=70, line_dash="dash", line_color="#16A34A",
                  annotation_text="Pass (70%)", annotation_position="right")
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        font=dict(color="#0F172A", family="Inter"),
        yaxis=dict(range=[0,115], gridcolor="#E2E8F0", ticksuffix="%",
                   title="Score", title_font_color="#475569"),
        xaxis=dict(gridcolor="#E2E8F0"),
        margin=dict(l=0, r=10, t=20, b=0),
        height=300,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Table
    with st.expander("📋 Full Score History"):
        disp = df[["chapter","score","total","percentage","date"]].copy()
        disp.columns = ["Chapter","Score","Total","Percentage (%)","Date"]
        st.dataframe(disp, use_container_width=True, hide_index=True)
else:
    st.info("📝 Take some quizzes to see your performance chart here.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Weak Topic Analysis ───────────────────────────────────────
st.markdown("#### 🧠 Weak Topic Analysis")
if st.button("🔍 Analyse My Weak Topics", type="primary"):
    with st.spinner("Analysing your query patterns…"):
        try:
            r = httpx.get(f"{BACKEND}/api/analytics/weak-topics/{SID}", timeout=60)
            st.session_state["_weak"] = r.json()
        except Exception as e:
            st.error(str(e))

if "_weak" in st.session_state:
    w = st.session_state["_weak"]
    st.markdown(
        f"""
        <div class="card card-accent">
            <div style="font-weight:600; color:#0F172A; margin-bottom:0.5rem;">
                Analysis based on {w.get("query_count",0)} questions
            </div>
            <div style="color:#475569; line-height:1.8; white-space:pre-wrap;
                        font-size:0.9rem;">{w.get("analysis","No analysis yet.")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── System Health ─────────────────────────────────────────────
st.markdown("#### 🔧 System Health")
try:
    health = httpx.get(f"{BACKEND}/health", timeout=5).json()
    ok = health.get("status") == "healthy"

    c1, c2, c3 = st.columns(3, gap="medium")
    for col, icon, title, val, color in [
        (c1, "🖥️", "Backend",      "HEALTHY" if ok else "UNHEALTHY",
         "#16A34A" if ok else "#DC2626"),
        (c2, "🗄️", "Vector Store", f'{health.get("vector_store_docs",0)} chunks', "#4F46E5"),
        (c3, "🤖", "LLM",          health.get("llm_backend","?").upper(), "#0EA5E9"),
    ]:
        col.markdown(
            f'<div class="card" style="text-align:center; padding:1rem;">'
            f'<div style="font-size:1.4rem;">{icon}</div>'
            f'<div style="font-weight:600; color:#0F172A; margin:0.25rem 0 0.15rem;">{title}</div>'
            f'<div style="color:{color}; font-size:0.85rem; font-weight:600;">{val}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
except Exception:
    st.warning("⚠️ Start the backend to see system health.")
