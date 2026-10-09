@echo off
REM Paso 7: cuenta filas en H2 y MySQL. Falla si no coinciden.
setlocal
cd /d "%~dp0.."
call "%~dp0_py.bat"
if errorlevel 1 exit /b 1
"%PY%" python\verificar.py
exit /b %errorlevel%
