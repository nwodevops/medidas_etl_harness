@echo off
REM init.bat — Harness Windows. Equivalente de init.sh.
REM Uso: init.bat [local|remote]   (default: remote)
REM H2 mem:csep:9092 es compartido. Esta corrida encadena los pasos sin salir.
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "ENV=%~1"
if "%ENV%"=="" set "ENV=remote"
echo ==^> Harness Windows medidas: entorno %ENV%

set "PY=%~dp0.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

set "LOGDIR=%~dp0logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd"') do set "STAMP=%%a"
set "LOGFILE=%LOGDIR%\init_%STAMP%.log"
set "RUNLOG=%TEMP%\medidas_run_%RANDOM%.log"
set "STEPLOG=%TEMP%\medidas_step_%RANDOM%.log"
echo === inicio %date% %time% env=%ENV% === > "%RUNLOG%"
echo === inicio %date% %time% env=%ENV% ===

echo ==^> Prerrequisitos
java -version >nul 2>&1
if errorlevel 1 (
  echo FAIL: java no esta en PATH
  goto :fail
)
if not exist "%~dp0h2\lib\h2-2.4.240.jar" (
  echo FAIL: jar H2 no encontrado en h2\lib
  goto :fail
)
"%PY%" -c "import yaml,pandas,jaydebeapi,pymysql,gspread,openpyxl" >nul 2>&1
if errorlevel 1 (
  echo FAIL: %PY% no tiene las dependencias de python\requirements.txt
  goto :fail
)
if not exist "%~dp0client_secret.json" (
  echo FAIL: falta client_secret.json
  goto :fail
)
echo ==^> switch-env %ENV%
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0switch-env.ps1" %ENV%
if errorlevel 1 (
  echo FAIL: switch-env %ENV%
  goto :fail
)

set "SCHEMA="
for /f "usebackq delims=" %%v in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\get_var.ps1" "%~dp0project-config.json" DB_MYSQL_DW_DATABASE`) do set "SCHEMA=%%v"
if "%SCHEMA%"=="" (
  echo FAIL: no pude resolver la base destino MySQL
  goto :fail
)
echo ==^> Base destino MySQL: %SCHEMA%

echo ==^> Paso 1/7: Reset H2 clean
echo ==^> Paso 1/7: Reset H2 clean>> "%RUNLOG%"
call :runstep "%~dp0scripts\step_reset_h2.bat"
if errorlevel 1 goto :fail

echo ==^> Paso 2/7: Python create STG
echo ==^> Paso 2/7: Python create STG>> "%RUNLOG%"
call :runstep "%~dp0scripts\step_create_stg.bat"
if errorlevel 1 goto :fail

echo ==^> Paso 3/7: Cargar Sheets suscripcion
echo ==^> Paso 3/7: Cargar Sheets suscripcion>> "%RUNLOG%"
call :runstep "%~dp0scripts\step_cargar_suscripcion.bat"
if errorlevel 1 goto :fail

echo ==^> Paso 4/7: Cargar Sheets seguimiento
echo ==^> Paso 4/7: Cargar Sheets seguimiento>> "%RUNLOG%"
call :runstep "%~dp0scripts\step_cargar_seguimiento.bat"
if errorlevel 1 goto :fail

echo ==^> Paso 5/7: Cargar Sheets od
echo ==^> Paso 5/7: Cargar Sheets od>> "%RUNLOG%"
call :runstep "%~dp0scripts\step_cargar_od.bat"
if errorlevel 1 goto :fail

echo ==^> Paso 6/7: Python main
echo ==^> Paso 6/7: Python main>> "%RUNLOG%"
call :runstep "%~dp0scripts\step_main.bat"
if errorlevel 1 goto :fail

findstr /c:"${" "%RUNLOG%" >nul 2>&1
if not errorlevel 1 (
  echo FAIL: el log contiene variables Hop sin resolver
  goto :fail
)

echo ==^> Paso 7/7: Verificar conteos en H2 y MySQL
echo ==^> Paso 7/7: Verificar conteos>> "%RUNLOG%"
call :runstep "%~dp0scripts\step_verificar.bat"
if errorlevel 1 goto :fail

echo.
echo HARNESS OK -^> conteos leidos de H2 y MySQL. Bitacora: %LOGFILE%
echo.>> "%RUNLOG%"
echo HARNESS OK base %SCHEMA%>> "%RUNLOG%"
call :savelog
endlocal
exit /b 0

:runstep
call "%~1" > "%STEPLOG%" 2>&1
set "RC=%ERRORLEVEL%"
type "%STEPLOG%"
type "%STEPLOG%" >> "%RUNLOG%"
exit /b %RC%

:savelog
if exist "%RUNLOG%" type "%RUNLOG%" >> "%LOGFILE%"
if exist "%RUNLOG%" del /q "%RUNLOG%" >nul 2>&1
if exist "%STEPLOG%" del /q "%STEPLOG%" >nul 2>&1
exit /b 0

:fail
echo.
echo HARNESS FAIL -^> revisa el error de arriba. Bitacora: %LOGFILE%
echo HARNESS FAIL>> "%RUNLOG%"
call :savelog
endlocal
exit /b 1
