@echo off
echo build archive file ...

set path=C:\Program Files\7-Zip;%path%
7z a OSFP-DEBUG-GUI.7z ".\router" ".\static" ".\templates" "clean.bat" "Reload.bat" "Config.ini" "OSFP-DEBUG-GUI-Starter.bat" "fixed_freq.py" "scan_freq.py" "run.py" 

echo build ok!

pause
