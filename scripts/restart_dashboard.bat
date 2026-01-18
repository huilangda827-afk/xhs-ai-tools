@echo off
REM 快速重启 Dashboard 脚本
echo ========================================
echo 🔄 重启 Streamlit Dashboard
echo ========================================
echo.

cd /d D:\multisim\MediaCrawler-main

echo 🧹 清理 Streamlit 缓存...
uv run streamlit cache clear

echo.
echo 🚀 启动 Dashboard...
echo 浏览器将自动打开 http://localhost:8501
echo.

uv run python -m streamlit run src/app/dashboard.py

pause
