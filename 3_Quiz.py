"""
frontend/pages/3_Quiz.py — Clean light quiz page
"""
import streamlit as st
import httpx
from pathlib import Path

st.set_page_config(page_title="Quiz · RAG Tutor", page_icon="📝", layout="wide")
css = Path(__file__).parent.parent / "assets" / "style.css"
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

for k, v in {
    "backend_url": "http://localhost:8000", "session_id": "session_001",
    "quiz_questions": [], "quiz_answers": {}, "quiz_submitted": False,
    "quiz_result": None, "quiz_chapter": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

BACKEND = st.session_state.backend_url

# Header
st.markdown("""
<div class="page-header">
    <div class="page-title">📝 Chapter Quiz</div>
    <div class="page-subtitle">Test your knowledge with AI-generated MCQs</div>
</div>
""", unsafe_allow_html=True)

# Sidebar settings
with st.sidebar:
    st.markdown("### Quiz Settings")
    try:
        chapters = httpx.get(f"{BACKEND}/api/upload/chapters", timeout=4).json().get("chapters", [])
    except Exception:
        chapters = ["Current Electricity", "Moving Charges and Magnetism"]

    chapter = st.selectbox("Chapter", chapters if chapters else ["Upload a PDF first"])
    num_q   = st.slider("Questions", 3, 10, 5)
    diff    = st.select_slider("Difficulty", ["easy", "medium", "hard"], "medium")

    st.divider()
    gen_btn = st.button("🎲 Generate Quiz", type="primary", use_container_width=True)

    if st.button("🔄 Reset", use_container_width=True):
        for k in ["quiz_questions","quiz_answers","quiz_submitted","quiz_result"]:
            st.session_state[k] = [] if k == "quiz_questions" else ({} if k == "quiz_answers" else (False if k == "quiz_submitted" else None))
        st.rerun()

# Generate
if gen_btn and chapters:
    with st.spinner(f"Generating {num_q} {diff} questions for '{chapter}'…"):
        try:
            resp = httpx.post(f"{BACKEND}/api/quiz/generate", json={
                "chapter_name": chapter, "num_questions": num_q,
                "difficulty": diff, "session_id": st.session_state.session_id,
            }, timeout=90)
            if resp.status_code == 200:
                d = resp.json()
                st.session_state.quiz_questions = d["questions"]
                st.session_state.quiz_answers   = {}
                st.session_state.quiz_submitted  = False
                st.session_state.quiz_result     = None
                st.session_state.quiz_chapter    = chapter
                st.success(f"✅ Generated {len(d['questions'])} questions!")
                st.rerun()
            else:
                st.error(resp.json().get("detail", "Generation failed"))
        except httpx.ConnectError:
            st.error("❌ Backend not running.")
        except Exception as e:
            st.error(str(e))

# Quiz display
qs = st.session_state.quiz_questions
if qs:
    answered = len(st.session_state.quiz_answers)
    total    = len(qs)
    submitted = st.session_state.quiz_submitted
    result    = st.session_state.quiz_result

    # Progress
    st.markdown(f"**Progress:** {answered} / {total} answered")
    st.progress(answered / total if total else 0)
    st.markdown("<br>", unsafe_allow_html=True)

    for q in qs:
        qn   = q.get("question_number", 1)
        opts = q.get("options", {})
        corr = q.get("correct_answer", "")
        expl = q.get("explanation", "")

        # Card style
        card_extra = ""
        if submitted and result:
            fb = next((f for f in result.get("feedback", []) if f["question_number"] == qn), None)
            if fb:
                card_extra = "quiz-correct" if fb["is_correct"] else "quiz-incorrect"

        st.markdown(f'<div class="quiz-card {card_extra}">', unsafe_allow_html=True)
        st.markdown(f"**Q{qn}.** {q['question']}")

        if not submitted:
            sel = st.radio(
                f"q{qn}", sorted(opts.keys()),
                format_func=lambda k: f"{k})  {opts.get(k,'')}",
                key=f"qr_{qn}", horizontal=True, label_visibility="collapsed",
            )
            if sel:
                st.session_state.quiz_answers[qn] = sel
        else:
            student = st.session_state.quiz_answers.get(qn, "—")
            cols = st.columns(len(opts))
            for j, k in enumerate(sorted(opts.keys())):
                with cols[j]:
                    if k == corr:
                        color = "#16A34A"; weight = "bold"
                    elif k == student and k != corr:
                        color = "#DC2626"; weight = "bold"
                    else:
                        color = "#475569"; weight = "normal"
                    st.markdown(
                        f'<span style="color:{color};font-weight:{weight};">{k}) {opts[k]}</span>',
                        unsafe_allow_html=True,
                    )
            if expl:
                st.markdown(
                    f'<div style="margin-top:0.5rem;padding:0.5rem 0.75rem;'
                    f'background:#F1F5F9;border-radius:8px;'
                    f'font-size:0.84rem;color:#475569;">💡 {expl}</div>',
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # Submit
    if not submitted:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2,1,2])
        with c2:
            if st.button("📊 Submit", type="primary", use_container_width=True):
                if answered < total:
                    st.warning(f"Please answer all {total} questions first.")
                else:
                    with st.spinner("Scoring…"):
                        try:
                            resp = httpx.post(f"{BACKEND}/api/quiz/submit", json={
                                "session_id": st.session_state.session_id,
                                "chapter_name": st.session_state.quiz_chapter,
                                "answers": {str(k): v for k,v in st.session_state.quiz_answers.items()},
                                "questions": qs,
                            }, timeout=30)
                            if resp.status_code == 200:
                                st.session_state.quiz_result    = resp.json()
                                st.session_state.quiz_submitted = True
                                st.rerun()
                        except Exception as e:
                            st.error(str(e))

    # Results banner
    if submitted and result:
        st.divider()
        pct   = result["percentage"]
        score = result["score"]
        total_q = result["total"]
        color = "#16A34A" if pct >= 70 else "#D97706" if pct >= 40 else "#DC2626"
        emoji = "🎉" if pct >= 70 else "📚" if pct >= 40 else "💪"
        msg   = ("Excellent work!" if pct >= 70
                 else "Good effort — review weak areas." if pct >= 40
                 else "Keep practicing — check chapter summaries.")

        st.markdown(
            f"""
            <div class="card" style="text-align:center; border-top:3px solid {color}; padding:2rem;">
                <div style="font-size:2.5rem;">{emoji}</div>
                <div style="font-size:2.2rem; font-weight:700; color:{color};">{pct:.0f}%</div>
                <div style="color:#0F172A; font-size:1rem; font-weight:600;">{score} / {total_q} correct</div>
                <div style="color:#94A3B8; margin-top:0.4rem; font-size:0.88rem;">{msg}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    if not chapters:
        st.info("📤 Upload a NCERT PDF first, then generate a quiz.")
    else:
        st.markdown(
            """
            <div style="text-align:center; padding:4rem 1rem; color:#94A3B8;">
                <div style="font-size:2.5rem;">📝</div>
                <div style="font-size:0.95rem; color:#4F46E5; margin-top:1rem; font-weight:500;">
                    Configure settings in the sidebar and click Generate Quiz
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
