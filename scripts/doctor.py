# -*- coding: utf-8 -*-
"""
Environment Doctor - 环境自检脚本

功能：
- 检查 Python 解释器路径（确保在 .venv 中）
- 检查关键依赖是否安装
- 给出一键修复命令
"""
import sys
import os
from pathlib import Path


def main():
    print("=" * 70)
    print("🔍 环境自检 - Environment Doctor")
    print("=" * 70)
    
    # === 1. Python 解释器检查 ===
    print("\n📍 Python 解释器:")
    print(f"  路径: {sys.executable}")
    print(f"  版本: {sys.version.split()[0]}")
    
    # 判断是否在虚拟环境中
    in_venv = ".venv" in sys.executable or "venv" in sys.executable
    in_conda = "anaconda" in sys.executable.lower() or "conda" in sys.executable.lower()
    
    if in_venv:
        print("  状态: ✅ 使用虚拟环境（推荐）")
    elif in_conda:
        print("  状态: ⚠️  使用 Anaconda 环境（可能导致依赖冲突）")
        print("  建议: 使用 'uv venv' 创建独立虚拟环境")
    else:
        print("  状态: ⚠️  使用系统 Python（不推荐）")
        print("  建议: 使用 'uv venv' 创建虚拟环境")
    
    # === 2. 工作目录检查 ===
    print("\n📁 工作目录:")
    cwd = os.getcwd()
    print(f"  当前: {cwd}")
    
    has_pyproject = os.path.exists("pyproject.toml")
    has_requirements = os.path.exists("requirements.txt")
    
    if has_pyproject or has_requirements:
        print("  状态: ✅ 在项目根目录")
    else:
        print("  状态: ❌ 不在项目根目录")
        print("  建议: cd 到项目根目录（有 pyproject.toml 的地方）")
    
    # === 3. 关键模块导入检查 ===
    print("\n📦 核心模块检查:")
    
    core_modules = [
        ("src.crawler.xhs_adapter", "Stage-1: 爬虫"),
        ("src.pipeline.cleaner", "Stage-2: 清洗"),
        ("src.graph.builder", "Stage-3: 图构建"),
        ("src.graph.analytics", "Stage-3: 分析"),
        ("src.graph.visualizer", "Stage-3: 可视化"),
        ("src.generator.template_engine", "Stage-5: 文案生成"),
        ("src.app.components.insights", "洞察面板"),
        ("src.utils.packaging", "工具: 打包"),
        ("src.generator.llm_client", "LLM 客户端（可选）"),
    ]
    
    module_ok = True
    for module_name, desc in core_modules:
        try:
            __import__(module_name)
            print(f"  ✅ {desc:25s}")
        except ImportError as e:
            print(f"  ❌ {desc:25s} - {e}")
            module_ok = False
    
    # === 4. 关键依赖检查 ===
    print("\n🔧 关键依赖检查:")
    
    critical_deps = [
        ("streamlit", "Streamlit Dashboard"),
        ("google.protobuf", "Protobuf (streamlit 依赖)"),
        ("networkx", "图谱构建"),
        ("pyvis", "图谱可视化"),
        ("scipy", "图谱算法"),
        ("pandas", "数据处理"),
    ]
    
    missing = []
    for module_name, desc in critical_deps:
        try:
            # 特殊处理 google.protobuf
            if module_name == "google.protobuf":
                __import__("google.protobuf")
            else:
                mod = __import__(module_name)
            
            version = getattr(mod, "__version__", "unknown")
            print(f"  ✅ {desc:30s} ({module_name}) - {version}")
        except ImportError:
            print(f"  ❌ {desc:30s} ({module_name}) - 未安装")
            missing.append(module_name)
    
    # === 5. 数据文件检查 ===
    print("\n📄 数据文件检查:")
    
    data_files = [
        ("data/raw/annotations.jsonl", "原始数据"),
        ("data/clean/annotations_clean.jsonl", "清洗数据"),
        ("data/samples/annotations_sample.jsonl", "样例数据"),
    ]
    
    for path, desc in data_files:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    count = sum(1 for _ in f)
                print(f"  ✅ {desc:20s} - {count} 条")
            except:
                print(f"  ⚠️  {desc:20s} - 存在但无法读取")
        else:
            print(f"  ❌ {desc:20s} - 不存在")
    
    # === 6. 总结与修复建议 ===
    print("\n" + "=" * 70)
    
    if not module_ok:
        print("❌ 核心模块导入失败")
        print("\n🔧 可能原因:")
        print("  1. 项目目录结构不完整")
        print("  2. 某些文件缺失或语法错误")
        print("\n  建议检查上述失败的模块文件是否存在")
    
    elif missing:
        print("❌ 发现缺失依赖")
        print("\n🔧 一键修复命令:")
        
        # 根据包名映射到安装包名
        install_names = []
        for mod in missing:
            if mod == "google.protobuf":
                install_names.append("protobuf")
            else:
                install_names.append(mod)
        
        print(f"\n  uv pip install {' '.join(install_names)}")
        print("\n或安装完整依赖:")
        print("\n  uv pip install -r requirements.txt")
    
    elif not in_venv:
        print("⚠️  建议使用虚拟环境")
        print("\n🔧 推荐操作:")
        print("\n  uv venv")
        print("  uv pip install -r requirements.txt")
        print("  uv run python scripts/doctor.py")
    
    else:
        print("✅ 所有检查通过！")
        print("\n🚀 可以启动 Dashboard:")
        print("\n  uv run python -m streamlit run src/app/dashboard.py")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
