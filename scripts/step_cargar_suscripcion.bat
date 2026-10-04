@echo off
REM Paso 3: Google Sheets familia suscripcion -> STG_MED_SUSC_*.
setlocal
cd /d "%~dp0.."
call "%~dp0_py.bat"
if errorlevel 1 exit /b 1
"%PY%" python\cargar_sheets.py suscripcion
exit /b %errorlevel%
