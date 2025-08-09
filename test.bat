@'
@echo off
echo Testing Tinder Bot Installation...
call venv\Scripts\activate.bat
python -c "import flask; print('OK: Flask installed')"
python -c "from config import config; print('OK: Configuration loads')"
pause
'@ | Out-File -FilePath "test.bat" -Encoding ASCII
