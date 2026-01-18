# -*- coding: utf-8 -*-
"""简单的清洗脚本运行器"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline.cleaner import main

if __name__ == "__main__":
    main()
