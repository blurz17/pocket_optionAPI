@echo off
title Pocket Option Market Data Harvester
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_dashboard.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Dashboard exited or encountered an error.
    pause
)
