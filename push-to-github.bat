@echo off
chcp 65001
echo ======================================
echo  提交代码到 GitHub
echo ======================================
cd /d "e:\CodeTest\Sidereus笔试"

echo.
echo [1/3] 提交代码...
git commit -m "Initial commit"

echo.
echo [2/3] 切换到 main 分支...
git branch -M main

echo.
echo [3/3] 推送到 GitHub...
git push -u origin main

echo.
echo ======================================
echo  完成！
echo ======================================
pause
