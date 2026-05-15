"""
frontend/pages/2_Upload.py — Clean light upload page
"""
import time
import streamlit as st
import httpx
from pathlib import Path

st.set_page_config(page_title="Upload · RAG Tutor", page_icon="📤", layout="wide")
css = Path(__file__).parent.parent / "assets" / "style.css"
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

for k, v in {"backend_url": "http://localhost:8000", "session_id": "session_001"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

BACKEND = st.session_state.backend_url

# Header
st.markdown("""
<div class="page-header">
    <div class="page-title">📤 Upload NCERT PDFs</div>
    <div class="page-subtitle">Upload chapter PDFs to build your AI knowledge base</div>
</div>
""", unsafe_allow_html=True)

# Where to get PDFs
with st.expander("📋 Where to download NCERT PDFs?"):
    st.markdown("""
**Download free from NCERT:**
1. Go to [ncert.nic.in/textbook.php?leph1=0-16](https://ncert.nic.in/textbook.php?leph1=0-16)
2. Download **Chapter 3** → `leph103.pdf` (Current Electricity)
3. Download **Chapter 4** → `leph104.pdf` (Moving Charges and Magnetism)
4. Upload them below

The system will automatically extract, chunk, embed, and store the content.
""")

st.markdown("---")

# Upload widget
st.markdown("#### Upload a PDF")
uploaded = st.file_uploader(
    "Choose a NCERT Physics PDF",
    type=["pdf"],
    help="Upload Chapter 3 or Chapter 4",
)

if uploaded:
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        st.markdown(
            f'<div class="card" style="padding:0.75rem 1rem;">'
            f'📄 <strong>{uploaded.name}</strong>'
            f'<span class="badge badge-primary" style="margin-left:0.5rem;">'
            f'{uploaded.size/1024:.0f} KB</span></div>',
            unsafe_allow_html=True,
        )
    with c2:
        process = st.button("🚀 Process", type="primary", use_container_width=True)

    if process:
        with st.status("Processing PDF…", expanded=True) as status:
            st.write("📖 Extracting text…")
            try:
                files = {"file": (uploaded.name, uploaded.getvalue(), "application/pdf")}
                resp = httpx.post(f"{BACKEND}/api/upload/", files=files, timeout=120)

                if resp.status_code == 200:
                    d = resp.json()
                    st.write("🧩 Chunking & embedding…")
                    time.sleep(0.3)
                    status.update(label="✅ Done!", state="complete")
                    st.success(d["message"])

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Pages",   d["total_pages"])
                    m2.metric("Chunks",  d["total_chunks"])
                    m3.metric("Words",   f'{d["total_words"]:,}')
                    m4.metric("Chapter", d["chapter_name"][:18])

                elif resp.status_code == 409:
                    status.update(label="Already uploaded", state="error")
                    st.warning(resp.json().get("detail", "Duplicate file."))
                else:
                    status.update(label="Failed", state="error")
                    st.error(resp.json().get("detail", "Unknown error"))

            except httpx.ConnectError:
                status.update(label="Connection failed", state="error")
                st.error("Backend not running. Start it with:\n```\npython -m uvicorn backend.main:app --reload\n```")
            except Exception as e:
                status.update(label="Error", state="error")
                st.error(str(e))

st.markdown("---")

# Uploaded documents
st.markdown("#### 📚 Uploaded Documents")

try:
    docs = httpx.get(f"{BACKEND}/api/upload/documents", timeout=6).json()
    if docs:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Documents", len(docs))
        c2.metric("Total Chunks", sum(d.get("total_chunks", 0) for d in docs))
        c3.metric("Total Pages",  sum(d.get("total_pages",  0) for d in docs))
        st.markdown("<br>", unsafe_allow_html=True)
        for d in docs:
            st.markdown(
                f'<div class="card card-accent" style="margin-bottom:0.65rem;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div><strong>{d["filename"]}</strong><br>'
                f'<span class="badge badge-primary" style="margin-top:0.25rem;">{d["chapter_name"]}</span></div>'
                f'<div style="text-align:right;color:#94A3B8;font-size:0.8rem;">'
                f'{d["total_pages"]} pages · {d["total_chunks"]} chunks<br>'
                f'{str(d.get("upload_timestamp",""))[:10]}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No documents uploaded yet. Upload your first NCERT PDF above.")
except Exception:
    st.warning("⚠️ Start the backend server to see uploaded documents.")

st.markdown("---")

# Vector store stats
st.markdown("#### 🗄️ Vector Store Status")
c1, c2 = st.columns(2)
with c1:
    try:
        stats = httpx.get(f"{BACKEND}/api/upload/stats", timeout=6).json()
        st.markdown(
            f'<div class="card">'
            f'<div style="font-weight:600;color:#0F172A;margin-bottom:0.5rem;">ChromaDB Collection</div>'
            f'<div><strong>Total Chunks:</strong> {stats.get("total_chunks",0)}</div>'
            f'<div><strong>Chapters:</strong> {", ".join(stats.get("chapters",[]))  or "None yet"}</div>'
            f'<div><strong>Sources:</strong> {", ".join(stats.get("sources",[])) or "None yet"}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.info("Start backend to see vector store stats.")

with c2:
    st.markdown(
        """
        <div class="card">
            <div style="font-weight:600;color:#0F172A;margin-bottom:0.5rem;">Processing Pipeline</div>
            <ol style="color:#475569; font-size:0.87rem; line-height:2; margin:0; padding-left:1.2rem;">
                <li>Text extraction (pdfplumber)</li>
                <li>Cleaning &amp; normalization</li>
                <li>Semantic chunking (500 chars, 100 overlap)</li>
                <li>Embedding (all-MiniLM-L6-v2)</li>
                <li>ChromaDB vector storage</li>
                <li>SQLite metadata storage</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )
