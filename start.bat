@echo off
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "Get-Content 'start.ps1' -Encoding UTF8 -Raw | Invoke-Expression"
