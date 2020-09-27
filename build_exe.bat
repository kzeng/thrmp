@echo off
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "datestamp=%YYYY%%MM%%DD%" & set "timestamp=%HH%%Min%%Sec%"
set "fullstamp=%YYYY%_%MM%_%DD%_%HH%_%Min%_%Sec%"

echo -------------------------------------------------
echo osfp-denug-gui packaging ...
echo -------------------------------------------------
python setup.py build

echo -------------------------------------------------
echo compile python source code ...
echo -------------------------------------------------
python compile.py
rem echo -------------------------------------------------
rem echo use python source code (NOT COMPILE) ...
rem echo ---------------------------------------- ---------

echo -------------------------------------------------
echo auto-update version ...
echo -------------------------------------------------
python auto_version.py %fullstamp%

echo -------------------------------------------------
echo add to zip file ...
echo -------------------------------------------------
set path=C:\Program Files\7-Zip;%path%
7z a -t7z -mx9 -r OSFP-DEBUG-GUI-[Alpha-EVB2]-%fullstamp%.7z ./build/exe.win-amd64-3.6
echo ziped ok

rem echo -------------------------------------------------
rem echo building OSFP-Debug-GUI installation package ...
rem echo -------------------------------------------------
rem "d:\NSIS\makensis.exe"  /NOTIFYHWND 722910 /DVERSION=%fullstamp% osfp-debug-gui-3.0.0

echo -------------------------------------------------
echo Skip building OSFP-Debug-GUI installation package ...
echo -------------------------------------------------


echo -------------------------------------------------
echo copying to share folder ...
echo -------------------------------------------------
echo share folder 'W:\Wuhan Shared Folder\to Kai\GUI-repo\OSFP-Debug-GUI-NF' ...
xcopy OSFP-DEBUG-GUI-[Alpha-EVB2]-%fullstamp%.7z "W:\Wuhan Shared Folder\to Kai\GUI-repo\OSFP-Debug-GUI-NF" /Y
rem xcopy OSFP-DEBUG-GUI-[Alpha-EVB2]-Setup-%fullstamp%.exe "W:\Wuhan Shared Folder\to Kai\GUI-repo\OSFP-Debug-GUI-NF" /Y


echo .
echo packaging ok!