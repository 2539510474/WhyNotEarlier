@echo off
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

if exist "%STARTUP%\woqu.vbs" (
    del "%STARTUP%\woqu.vbs"
    echo Removed!
) else (
    echo Not found.
)
pause
