@echo off
REM
REM This script only close current GUI-Window and GUI-Service 
REM That is to say kill all chrome.exe processes and current python.exe process
REM And Restart GUI-Service (python.exe process) and GUI-Window (chrome.exe process)
REM

echo Restart OSFP Debug GUI ...

set webview_path=%cd%
rem echo %webview_path%

cd ..

set root=%cd%
set python_path=%cd%\Python36\Python36

rem current disk
rem %~d0

cd %cd%\OSFP-Debug-GUI

taskkill /F /FI "WINDOWTITLE eq OSFP/QSFP-DD*"
taskkill /IM "chrome.exe" /F

start "OSFP/QSFP-DD Debug GUI" "%python_path%\python.exe" -u "%webview_path%"\run.py

