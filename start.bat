@echo off
REM ============================================================
REM RAG Adaptive Learning System — Windows Startup Script
REM ============================================================

echo.
echo  ==========================================
echo   RAG-Based Adaptive Learning System
echo  ==========================================
echo.

REM Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found. Install Python 3.10+ first.
    pause
    exit /b 1
)

REM Create and activate virtual environment
IF NOT EXIST "venv" (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
)

echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [SETUP] Installing dependencies...
pip install -r requirements.txt --quiet

REM Copy .env if not exists
IF NOT EXIST ".env" (
    echo [SETUP] Creating .env from .env.example...
    copy .env.example .env
    echo [WARNING] Please edit .env and add your OPENAI_API_KEY
    notepad .env
)

REM Create data directories
IF NOT EXIST "data\uploads" mkdir "data\uploads"
IF NOT EXIST "vector_db\chroma_store" mkdir "vector_db\chroma_store"

echo.
echo [STARTING] FastAPI Backend on http://localhost:8000
start "FastAPI Backend" cmd /k "venv\Scripts\activate.bat && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 >nul

echo [STARTING] Streamlit Frontend on http://localhost:8501
start "Streamlit Frontend" cmd /k "venv\Scripts\activate.bat && streamlit run frontend/app.py"

echo.
echo  ==========================================
echo   System is starting!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:8501
echo   API Docs: http://localhost:8000/docs
echo  ==========================================
echo.
echo  Next steps:
echo  1. Open http://localhost:8501 in your browser
echo  2. Go to Upload PDFs and upload NCERT chapters
echo  3. Go to Chat and start asking questions!
echo.

pause
