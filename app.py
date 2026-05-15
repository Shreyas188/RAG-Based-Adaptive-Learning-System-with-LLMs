"""
frontend/app.py  — Home page (light, clean redesign)
"""
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="RAG Physics Learning System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────
css = Path(__file__).parent / "assets" / "style.css"
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────
for key, val in {
    "session_id": "session_001",
    "chat_messages": [],
    "current_chapter": "All Chapters",
    "quiz_questions": [],
    "quiz_answers": {},
    "quiz_submitted": False,
    "quiz_result": None,
    "flashcards": [],
    "flashcard_index": 0,
    "flashcard_revealed": False,
    "backend_url": "http://localhost:8000",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="padding:1.1rem 0 0.5rem; text-align:center;">
            <div style="font-size:2.2rem;">🔬</div>
            <div style="font-size:1rem; font-weight:700; color:#0F172A; margin-top:0.4rem;">
                RAG Physics Tutor
            </div>
            <div style="font-size:0.73rem; color:#94A3B8; margin-top:0.15rem;">
                NCERT Class 12 · AI-Powered
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("### Navigation")
    st.page_link("app.py",              label="🏠  Home")
    st.page_link("pages/1_Chat.py",     label="💬  Chat Assistant")
    st.page_link("pages/2_Upload.py",   label="📤  Upload PDFs")
    st.page_link("pages/3_Quiz.py",     label="📝  Take Quiz")
    st.page_link("pages/4_Summary.py",  label="📋  Chapter Summary")
    st.page_link("pages/5_Dashboard.py",label="📊  Dashboard")

    st.divider()
    st.markdown("### Settings")
    sid = st.text_input("Session ID", value=st.session_state.session_id)
    if sid != st.session_state.session_id:
        st.session_state.session_id = sid
        st.session_state.chat_messages = []
        st.rerun()

    url = st.text_input("Backend URL", value=st.session_state.backend_url)
    st.session_state.backend_url = url

    st.divider()
    st.caption("v1.0 · LangChain · ChromaDB · GPT")

# ── Main Content ──────────────────────────────────────────────
st.markdown(
    """
    <div class="page-header">
        <div class="page-title">🔬 RAG-Based Adaptive Learning System</div>
        <div class="page-subtitle">
            AI-powered NCERT Physics tutor · Retrieval-Augmented Generation
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Hero columns
col_l, col_r = st.columns([3, 2], gap="large")

with col_l:
    st.markdown(
        """
        <div class="card card-accent fade-up">
            <h3 style="margin-top:0; color:#4F46E5;">🎓 Your AI Physics Tutor</h3>
            <p style="color:#475569; line-height:1.75;">
                This system uses <strong style="color:#4F46E5;">Retrieval-Augmented Generation</strong>
                to answer your NCERT Physics questions with accuracy.
                Upload a chapter PDF, ask any question, and get answers with exact page references.
            </p>
            <ul style="color:#475569; line-height:2.1; margin:0.75rem 0 0; padding-left:1.25rem;">
                <li>📖 Semantic search over NCERT textbook content</li>
                <li>🤖 GPT-powered explanations and answers</li>
                <li>📝 Auto-generated quizzes and flashcards</li>
                <li>📊 Adaptive analytics and weak topic detection</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_r:
    st.markdown(
        """
        <div class="card fade-up" style="border-top:3px solid #0EA5E9;">
            <h3 style="margin-top:0; color:#0369A1;">📚 Supported Chapters</h3>
            <div style="margin-bottom:0.85rem; padding:0.75rem 1rem;
                        background:#F0F9FF; border-radius:8px;
                        border-left:3px solid #0EA5E9;">
                <div style="font-weight:600; color:#0F172A;">Chapter 3</div>
                <div style="color:#475569; font-size:0.88rem;">⚡ Current Electricity</div>
            </div>
            <div style="padding:0.75rem 1rem;
                        background:#EEF2FF; border-radius:8px;
                        border-left:3px solid #4F46E5;">
                <div style="font-weight:600; color:#0F172A;">Chapter 4</div>
                <div style="color:#475569; font-size:0.88rem;">🧲 Moving Charges &amp; Magnetism</div>
            </div>
            <p style="margin:0.85rem 0 0; font-size:0.78rem; color:#94A3B8; text-align:center;">
                Upload PDFs from ncert.nic.in to get started
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Quick start
st.markdown("### 🚀 Quick Start")
steps = [
    ("📤", "Upload PDF",       "Go to Upload PDFs and add NCERT chapters"),
    ("💬", "Ask Questions",    "Use Chat Assistant to ask any Physics question"),
    ("📝", "Take a Quiz",      "Generate AI MCQs and test your knowledge"),
    ("📋", "Read Summaries",   "Get concise summaries and flashcards"),
    ("📊", "Track Progress",   "View analytics and weak topic suggestions"),
]
cols = st.columns(5, gap="small")
for i, (icon, title, desc) in enumerate(steps):
    with cols[i]:
        st.markdown(
            f"""
            <div class="card" style="text-align:center; min-height:130px; padding:1rem 0.75rem;">
                <div style="font-size:1.6rem;">{icon}</div>
                <div style="font-weight:600; color:#0F172A; font-size:0.85rem;
                            margin:0.35rem 0 0.25rem;">{title}</div>
                <div style="color:#94A3B8; font-size:0.75rem; line-height:1.4;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# Tech stack
st.markdown("### 🛠️ Tech Stack")
techs = [
    "Python 3.11", "FastAPI", "Streamlit", "LangChain",
    "ChromaDB", "Sentence Transformers", "OpenAI GPT", "SQLite", "Docker",
]
badges = " ".join(
    f'<span class="badge badge-primary">{t}</span>' for t in techs
)
st.markdown(
    f'<div style="display:flex;flex-wrap:wrap;gap:0.4rem;">{badges}</div>',
    unsafe_allow_html=True,
)
