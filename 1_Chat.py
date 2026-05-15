"""
frontend/pages/1_Chat.py — Clean light chat interface
"""
import streamlit as st
import httpx
from pathlib import Path

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Chat · RAG Tutor", page_icon="💬", layout="wide")

css = Path(__file__).parent.parent / "assets" / "style.css"
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

# ── Session defaults ──────────────────────────────────────────
for key, val in {
    "chat_messages": [], "session_id": "session_001",
    "backend_url": "http://localhost:8000", "current_chapter": "All Chapters",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

BACKEND = st.session_state.backend_url

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💬 Chat Options")

    try:
        r = httpx.get(f"{BACKEND}/api/upload/chapters", timeout=4)
        chapters = ["All Chapters"] + r.json().get("chapters", [])
    except Exception:
        chapters = ["All Chapters", "Current Electricity", "Moving Charges and Magnetism"]

    chapter = st.selectbox("Filter by Chapter", chapters,
                           help="Restrict answers to one chapter")
    top_k = st.slider("Context chunks", 1, 10, 5,
                      help="Number of text chunks retrieved per query")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        try:
            httpx.delete(f"{BACKEND}/api/chat/history/{st.session_state.session_id}", timeout=5)
        except Exception:
            pass
        st.session_state.chat_messages = []
        st.rerun()

    st.divider()
    st.markdown("**Sample Questions**")
    samples = [
        "What is Ohm's Law?",
        "Explain drift velocity.",
        "What is the right-hand thumb rule?",
        "Define magnetic flux density.",
        "State Kirchhoff's laws.",
    ]
    for q in samples:
        if st.button(q, key=f"sq_{q[:15]}", use_container_width=True):
            st.session_state["_prefill"] = q
            st.rerun()

# ── Header ────────────────────────────────────────────────────
st.markdown(
    """
    <div class="page-header">
        <div class="page-title">💬 Chat Assistant</div>
        <div class="page-subtitle">Ask any NCERT Class 12 Physics question</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Chapter badge
if chapter != "All Chapters":
    st.markdown(
        f'<span class="badge badge-primary">📚 {chapter}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("&nbsp;", unsafe_allow_html=True)

# ── Chat messages ─────────────────────────────────────────────
msgs = st.session_state.chat_messages

if not msgs:
    st.markdown(
        """
        <div style="text-align:center; padding:3.5rem 1rem; color:#94A3B8;">
            <div style="font-size:2.5rem;">🤖</div>
            <div style="font-size:1.05rem; font-weight:600; color:#4F46E5; margin:0.75rem 0 0.3rem;">
                Hello! I'm your AI Physics Tutor.
            </div>
            <div style="font-size:0.88rem;">
                Ask me anything about NCERT Class 12 Physics.<br>
                Try: <em>"What is Ohm's Law?"</em>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for msg in msgs:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            st.markdown(
                f'<div class="chat-user"><span style="font-size:0.72rem;'
                f' opacity:0.85;">You</span><br>{content}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-assistant">'
                f'<span style="font-size:0.72rem; color:#4F46E5; font-weight:600;">🤖 AI Tutor</span>'
                f'<br>{content}</div>',
                unsafe_allow_html=True,
            )

            # Confidence badge
            conf = msg.get("confidence", 0)
            if conf > 0:
                cls  = "badge-success" if conf >= 0.7 else "badge-warning" if conf >= 0.4 else "badge-danger"
                label = f"Confidence: {conf:.0%}"
                st.markdown(
                    f'<span class="badge {cls}" style="font-size:0.72rem;">{label}</span>',
                    unsafe_allow_html=True,
                )

            # Sources
            srcs = msg.get("sources", [])
            if srcs:
                with st.expander(f"📚 {len(srcs)} source(s) used"):
                    for s in srcs:
                        st.markdown(
                            f'<div class="source-card">'
                            f'<strong>{s.get("chapter","?")}</strong> · '
                            f'Pages: {s.get("pages","N/A")} · '
                            f'Relevance: {s.get("relevance_score",0):.0%}'
                            f'<br><em style="color:#64748B;font-size:0.78rem;">'
                            f'"{s.get("text_preview","")[:120]}…"</em></div>',
                            unsafe_allow_html=True,
                        )

            if msg.get("warning"):
                st.caption(f"⚠️ {msg['warning']}")

        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

# ── Input form ────────────────────────────────────────────────
prefill = st.session_state.pop("_prefill", "")

with st.form("chat_form", clear_on_submit=True):
    c1, c2 = st.columns([6, 1])
    with c1:
        user_input = st.text_input(
            "Question",
            value=prefill,
            placeholder="Type your Physics question here…",
            label_visibility="collapsed",
        )
    with c2:
        send = st.form_submit_button("Send ➤", use_container_width=True)

if send and user_input.strip():
    st.session_state.chat_messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking…"):
        try:
            resp = httpx.post(
                f"{BACKEND}/api/chat/",
                json={
                    "query": user_input,
                    "chapter_filter": None if chapter == "All Chapters" else chapter,
                    "session_id": st.session_state.session_id,
                    "top_k": top_k,
                },
                timeout=60,
            )
            if resp.status_code == 200:
                d = resp.json()
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": d["answer"],
                    "sources": d.get("sources", []),
                    "confidence": d.get("confidence", 0),
                    "warning": d.get("warning"),
                })
            else:
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": f"⚠️ {resp.json().get('detail','Server error')}",
                    "sources": [],
                })
        except httpx.ConnectError:
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": "❌ Cannot connect to backend. Run `uvicorn backend.main:app --reload`",
                "sources": [],
            })
        except Exception as e:
            st.session_state.chat_messages.append({
                "role": "assistant", "content": f"❌ {e}", "sources": [],
            })
    st.rerun()
