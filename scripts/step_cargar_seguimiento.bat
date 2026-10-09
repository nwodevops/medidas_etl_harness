@echo off
REM Paso 4: Google Sheets familia seguimiento -> STG_MED_SEG_*.
setlocal
cd /d "%~dp0.."
call "%~dp0_py.bat"
if errorlevel 1 exit /b 1
"%PY%" python\cargar_sheets.py seguimiento
exit /b %errorlevel%
