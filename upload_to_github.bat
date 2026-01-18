@echo off
chcp 65001 >nul
echo ========================================
echo 正在初始化 Git 仓库并上传到 GitHub
echo ========================================
echo.

echo [1/5] 初始化 Git 仓库...
git init
if errorlevel 1 (
    echo 错误: Git 初始化失败
    pause
    exit /b 1
)
echo ✓ Git 仓库初始化成功
echo.

echo [2/5] 添加所有文件到暂存区...
git add .
if errorlevel 1 (
    echo 错误: 添加文件失败
    pause
    exit /b 1
)
echo ✓ 文件添加成功
echo.

echo [3/5] 提交文件...
git commit -m "First upload: 小红书数据挖掘分析工作站"
if errorlevel 1 (
    echo 错误: 提交失败，可能需要配置 Git 用户信息
    echo 请运行以下命令:
    echo   git config --global user.email "your@email.com"
    echo   git config --global user.name "Your Name"
    pause
    exit /b 1
)
echo ✓ 提交成功
echo.

echo [4/5] 创建 main 分支...
git branch -M main
if errorlevel 1 (
    echo 错误: 创建分支失败
    pause
    exit /b 1
)
echo ✓ main 分支创建成功
echo.

echo [5/5] 关联远程仓库...
git remote add origin https://github.com/huilangda827-afk/xhs-ai-tools.git
if errorlevel 1 (
    echo 注意: 远程仓库可能已存在，继续推送...
)
echo ✓ 远程仓库关联成功
echo.

echo [6/6] 推送到 GitHub...
echo 注意: 这可能需要几分钟时间，请耐心等待...
git push -u origin main
if errorlevel 1 (
    echo 错误: 推送失败
    echo 可能的原因:
    echo   1. 需要 GitHub 身份验证（会弹出浏览器窗口）
    echo   2. 远程仓库已存在内容，可能需要 force push
    echo   3. 网络连接问题
    pause
    exit /b 1
)
echo.
echo ========================================
echo ✓ 所有操作完成！
echo 项目已成功上传到 GitHub
echo 访问: https://github.com/huilangda827-afk/xhs-ai-tools
echo ========================================
pause
