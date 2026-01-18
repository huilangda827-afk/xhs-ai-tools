# -*- coding: utf-8 -*-
"""检查依赖"""
import sys
import os

# 添加项目根目录到 path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("Python:", sys.executable)
print("Project:", project_root)
print()

deps = [
    "streamlit",
    "networkx", 
    "pyvis",
    "scipy",
    "pandas",
    "pymongo",
    "bson",
    "playwright",
    "httpx",
]

for dep in deps:
    try:
        __import__(dep)
        print(f"✅ {dep}")
    except ImportError as e:
        print(f"❌ {dep}: {e}")

print()
print("检查爬虫模块...")
try:
    from src.crawler.xhs_adapter import XhsBasicCrawler
    print("✅ XhsBasicCrawler 可导入")
except ImportError as e:
    print(f"❌ XhsBasicCrawler: {e}")
