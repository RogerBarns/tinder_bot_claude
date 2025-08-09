@echo off
echo Fixing bot issues...

cd C:\Users\Anon\Downloads\tinder_bot_claude\

echo.
echo Checking for duplicate routes in web/app.py...
findstr /n "download-logs" web\app.py

echo.
echo If you see multiple lines above, you need to remove duplicate @app.route('/download-logs') definitions
echo.
echo For now, let's try running without mobile binding...
echo.

REM Create a temporary fix for mobile_requests.py
echo import requests > mobile_requests_temp.py
echo mobile_session = requests.Session() >> mobile_requests_temp.py
echo def get_mobile_local_ip(): return None >> mobile_requests_temp.py
echo class SourceIPAdapter: pass >> mobile_requests_temp.py
echo def bind_to_mobile_interface(session): return False >> mobile_requests_temp.py

echo.
echo Temporary fix created. Try running again.
pause