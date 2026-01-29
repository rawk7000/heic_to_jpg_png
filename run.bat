@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   HEIC to JPG/PNG Converter
echo ========================================
echo.

REM Pruefen ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH!
    pause
    exit /b 1
)

REM Virtual Environment erstellen falls nicht vorhanden
if not exist "venv" (
    echo [1/3] Erstelle Virtual Environment...
    python -m venv venv
    if errorlevel 1 (
        echo FEHLER: Konnte venv nicht erstellen!
        pause
        exit /b 1
    )
) else (
    echo [1/3] Virtual Environment existiert bereits.
)

REM Virtual Environment aktivieren
echo [2/3] Aktiviere Virtual Environment...
call venv\Scripts\activate.bat

REM Requirements installieren
echo [3/3] Installiere Abhangigkeiten...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo   Starte Konvertierung...
echo ========================================
echo.

REM Skript ausfuehren
python convert_heic.py

echo.
pause
