"""
frontend/pages/4_Summary.py — Clean light summary + flashcard page
"""
import streamlit as st
import httpx
from pathlib import Path

st.set_page_config(page_title="Summary · RAG Tutor", page_icon="📋", layout="wide")
css = Path(__file__).parent.parent / "assets" / "style.css"
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

for k, v in {
    "backend_url": "http://localhost:8000", "session_id": "session_001",
    "flashcards": [], "flashcard_index": 0, "flashcard_revealed": False,
    "current_summary": None, "summary_chapter_name": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

BACKEND = st.session_state.backend_url

st.markdown("""
<div class="page-header">
    <div class="page-title">📋 Summary & Flashcards</div>
    <div class="page-subtitle">AI-generated summaries, flashcards, and downloadable notes</div>
</div>
""", unsafe_allow_html=True)

try:
    chapters = httpx.get(f"{BACKEND}/api/upload/chapters", timeout=4).json().get("chapters", [])
except Exception:
    chapters = ["Current Electricity", "Moving Charges and Magnetism"]

tab1, tab2 = st.tabs(["📖 Chapter Summary", "🃏 Flashcards"])

# ── Summary Tab ───────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns([3, 1])
    with c1:
        sel_ch = st.selectbox("Chapter", chapters if chapters else ["Upload a PDF first"],
                              key="sum_ch")
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        gen_sum = st.button("📖 Generate", type="primary", use_container_width=True)

    if gen_sum and chapters:
        with st.spinner(f"Summarising '{sel_ch}'…"):
            try:
                resp = httpx.post(f"{BACKEND}/api/summary/",
                                  json={"chapter_name": sel_ch,
                                        "session_id": st.session_state.session_id},
                                  timeout=90)
                if resp.status_code == 200:
                    st.session_state.current_summary      = resp.json()
                    st.session_state.summary_chapter_name = sel_ch
                else:
                    st.error(resp.json().get("detail", "Failed"))
            except httpx.ConnectError:
                st.error("❌ Backend not running.")
            except Exception as e:
                st.error(str(e))

    if st.session_state.current_summary:
        s  = st.session_state.current_summary
        ch = st.session_state.summary_chapter_name

        st.markdown(
            f"""
            <div class="card card-accent" style="margin-top:1rem;">
                <h3 style="color:#4F46E5; margin-top:0;">📚 {ch}</h3>
                <div style="color:#0F172A; line-height:1.85; white-space:pre-wrap;
                            font-size:0.92rem;">{s.get("summary","No summary.")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        srcs = s.get("sources", [])
        if srcs:
            with st.expander("📚 Sources"):
                for src in srcs:
                    st.markdown(
                        f'<div class="source-card">📖 {src.get("chapter","?")} · '
                        f'Pages: {src.get("pages","N/A")}</div>',
                        unsafe_allow_html=True,
                    )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 Export Notes as PDF"):
            try:
                resp = httpx.post(f"{BACKEND}/api/summary/export-notes",
                                  json={"chapter_name": ch,
                                        "session_id": st.session_state.session_id},
                                  timeout=60)
                if resp.status_code == 200:
                    st.download_button("⬇️ Download PDF", resp.content,
                                       f"{ch}_notes.pdf", "application/pdf")
            except Exception as e:
                st.error(str(e))
    else:
        st.info("Select a chapter above and click Generate to see the summary.")

# ── Flashcards Tab ────────────────────────────────────────────
with tab2:
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        fc_ch = st.selectbox("Chapter", chapters if chapters else ["Upload a PDF first"],
                             key="fc_ch")
    with c2:
        n_cards = st.number_input("Cards", 3, 20, 10)
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        gen_fc = st.button("🃏 Generate", type="primary", use_container_width=True)

    if gen_fc and chapters:
        with st.spinner(f"Generating {n_cards} flashcards…"):
            try:
                resp = httpx.post(f"{BACKEND}/api/summary/flashcards",
                                  json={"chapter_name": fc_ch, "num_cards": n_cards,
                                        "session_id": st.session_state.session_id},
                                  timeout=90)
                if resp.status_code == 200:
                    st.session_state.flashcards        = resp.json().get("flashcards", [])
                    st.session_state.flashcard_index   = 0
                    st.session_state.flashcard_revealed = False
                    st.success(f"✅ {len(st.session_state.flashcards)} flashcards ready!")
                    st.rerun()
                else:
                    st.error(resp.json().get("detail", "Failed"))
            except Exception as e:
                st.error(str(e))

    cards = st.session_state.flashcards
    if cards:
        idx   = st.session_state.flashcard_index
        card  = cards[idx]
        total = len(cards)

        st.markdown(f"**Card {idx+1} of {total}**")
        st.progress((idx+1) / total)
        st.markdown("<br>", unsafe_allow_html=True)

        # Question card
        st.markdown(
            f"""
            <div class="flashcard">
                <div style="font-size:0.7rem; color:#4F46E5; font-weight:600;
                            text-transform:uppercase; letter-spacing:0.05em;
                            margin-bottom:0.5rem;">Question {idx+1}</div>
                <div style="color:#0F172A; font-size:1rem; font-weight:500;
                            line-height:1.65;">{card['question']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Answer
        if st.session_state.flashcard_revealed:
            st.markdown(
                f"""
                <div class="flashcard-answer">
                    <div style="font-size:0.7rem; color:#16A34A; font-weight:600;
                                text-transform:uppercase; letter-spacing:0.05em;
                                margin-bottom:0.4rem;">Answer</div>
                    <div style="color:#0F172A; line-height:1.65;">{card['answer']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("⬅ Prev", disabled=idx==0, use_container_width=True):
                st.session_state.flashcard_index -= 1
                st.session_state.flashcard_revealed = False
                st.rerun()
        with b2:
            label = "🙈 Hide Answer" if st.session_state.flashcard_revealed else "👁 Show Answer"
            if st.button(label, use_container_width=True):
                st.session_state.flashcard_revealed = not st.session_state.flashcard_revealed
                st.rerun()
        with b3:
            if st.button("Next ➜", disabled=idx==total-1, use_container_width=True):
                st.session_state.flashcard_index += 1
                st.session_state.flashcard_revealed = False
                st.rerun()

        # Export
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 Export Flashcards as PDF"):
            try:
                resp = httpx.post(f"{BACKEND}/api/summary/export-flashcards",
                                  json={"chapter_name": fc_ch, "num_cards": n_cards,
                                        "session_id": st.session_state.session_id},
                                  timeout=60)
                if resp.status_code == 200:
                    st.download_button("⬇️ Download Flashcard PDF", resp.content,
                                       f"{fc_ch}_flashcards.pdf", "application/pdf")
            except Exception as e:
                st.error(str(e))
    else:
        if not chapters:
            st.info("📤 Upload a NCERT PDF first.")
        else:
            st.info("Select a chapter and click Generate to create flashcards.")
