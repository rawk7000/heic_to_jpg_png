@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM Pruefen ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH!
    pause
    exit /b 1
)

REM Virtual Environment erstellen falls nicht vorhanden
if not exist "venv" (
    echo Erstelle Virtual Environment...
    python -m venv venv
    if errorlevel 1 (
        echo FEHLER: Konnte venv nicht erstellen!
        pause
        exit /b 1
    )
)

REM Virtual Environment aktivieren
call venv\Scripts\activate.bat

REM Requirements installieren
pip install -r requirements.txt --quiet

REM GUI starten
pythonw gui.py
