@echo off
REM Paso 6: cuenta filas en H2 y Oracle. Falla si no coinciden.
setlocal
cd /d "%~dp0.."
call "%~dp0_py.bat"
if errorlevel 1 exit /b 1
"%PY%" python\verificar.py
exit /b %errorlevel%
