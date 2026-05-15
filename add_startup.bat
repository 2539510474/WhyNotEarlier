@echo off
set SCRIPT=%~dp0woqu.py
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

echo Set s = CreateObject("WScript.Shell") > "%STARTUP%\woqu.vbs"
echo s.Run "pythonw ""%SCRIPT%""", 0, False >> "%STARTUP%\woqu.vbs"

echo Done! Added to startup.
pause
