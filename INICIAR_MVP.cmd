@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Falta el entorno Python. Consulta MVP_GONDOLAS.md para instalarlo.
  pause
  exit /b 1
)
if not exist "artifacts\models\gondola-yolo26n.pt" (
  echo Falta el modelo entrenado. Consulta MVP_GONDOLAS.md.
  pause
  exit /b 1
)
echo Gondola Vision - MVP
echo Cuando aparezca Application startup complete, abre http://127.0.0.1:8000/
echo Deja esta ventana abierta. Para detener el servidor, pulsa Ctrl+C.
".venv\Scripts\python.exe" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
pause
