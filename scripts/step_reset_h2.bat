@echo off
REM Paso 1: reset limpio de H2 (mem:csep, TCP 9092) + DDL.
setlocal
cd /d "%~dp0.."
call h2\scripts\reset_and_create.bat
exit /b %errorlevel%
