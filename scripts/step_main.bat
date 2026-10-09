@echo off
REM Paso 6: python\main.py -> logica\medidas.py -> MySQL DW_MED_*.
setlocal
cd /d "%~dp0.."
call "%~dp0_py.bat"
if errorlevel 1 exit /b 1
"%PY%" python\main.py
exit /b %errorlevel%
