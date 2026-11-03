@echo off
echo ============================================================
echo  Starting Football Match Predictor Frontend (React/Vite)
echo ============================================================
set "PATH=C:\Program Files\nodejs;%PATH%"
cd /d "%~dp0\frontend"

echo Running on http://localhost:5173
echo.
npm run dev
pause

