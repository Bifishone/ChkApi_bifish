@echo off
chcp 65001 > nul
echo.
set /p target=[*] 请输入需要检测的目标:
python3 ChkApi.py -u %target%
echo.
pause