@echo off
echo ============================================================
echo  Starting Football Match Predictor Backend (FastAPI)
echo ============================================================
set "PATH=C:\Users\allun\AppData\Local\Programs\Python\Python315;C:\Users\allun\AppData\Local\Programs\Python\Python315\Scripts;%PATH%"
cd /d "%~dp0"

echo Running on http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
pause
