@echo off
chcp 65001 > nul
echo. 

::清理缓存文件夹
rmdir /S /Q "results"
echo.

::清理一些txt文件
del /q result.txt


echo 清理完毕！！！
echo.