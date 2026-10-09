@echo off
REM Paso 5: Google Sheets familia od -> STG_MED_OD_*.
setlocal
cd /d "%~dp0.."
call "%~dp0_py.bat"
if errorlevel 1 exit /b 1
"%PY%" python\cargar_sheets.py od
exit /b %errorlevel%
