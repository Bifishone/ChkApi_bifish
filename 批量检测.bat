@echo off
chcp 65001 > nul
echo.
python3 ChkApi.py -f url.txt
echo.
pause