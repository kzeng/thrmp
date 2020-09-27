@echo off
echo Start GUI ...

set webview_path=%cd%
echo %webview_path%

cd ..

set root=%cd%
set python_path=%root%\Python36\Python36

rem current disk
rem %~d0

rem cd %cd%\OSFP-Debug-GUI
cd %webview_path%

rem set PYTHON to environment ariable 
set path=%python_path%;%path%
echo %path%

rem pause

start "GUI Service" "%python_path%\python.exe" -u "%webview_path%"\run.py
