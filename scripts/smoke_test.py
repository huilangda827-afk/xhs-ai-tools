# -*- coding: utf-8 -*-
"""
Smoke Test - 冒烟测试
快速验证核心功能是否正常（回归测试）

验证内容：
- 数据文件存在性和完整性
- 关键模块可导入
- 输出文件生成
"""
import os
import json
import sys


def test_data_files():
    """测试数据文件"""
    print("\n📄 数据文件检查:")
    
    checks = {
        "data/raw/annotations.jsonl": 1,          # 至少1行
        "data/clean/annotations_clean.jsonl": 1,  # 至少1行
        "data/samples/annotations_sample.jsonl": 20,  # 至少20行（样例）
        "data/stats/cleaning_report.json": 0,     # 存在即可
    }
    
    passed = 0
    total = len(checks)
    
    for path, min_lines in checks.items():
        if not os.path.exists(path):
            print(f"  ❌ {path} - 不存在")
            continue
        
        if min_lines == 0:
            print(f"  ✅ {path} - 存在")
            passed += 1
            continue
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = sum(1 for _ in f)
            
            if lines >= min_lines:
                print(f"  ✅ {path} - {lines} 条（要求 ≥{min_lines}）")
                passed += 1
            else:
                print(f"  ❌ {path} - {lines} 条（要求 ≥{min_lines}）")
        except Exception as e:
            print(f"  ❌ {path} - 读取失败: {e}")
    
    return passed, total


def test_output_files():
    """测试输出文件"""
    print("\n📊 输出文件检查:")
    
    checks = {
        "data/output/graph.html": 10 * 1024,  # 至少10KB
    }
    
    passed = 0
    total = len(checks)
    
    for path, min_size in checks.items():
        if not os.path.exists(path):
            print(f"  ⚠️  {path} - 不存在（需先运行 Mine）")
            continue
        
        size = os.path.getsize(path)
        size_kb = size / 1024
        
        if size >= min_size:
            print(f"  ✅ {path} - {size_kb:.1f} KB（要求 ≥{min_size/1024}KB）")
            passed += 1
        else:
            print(f"  ❌ {path} - {size_kb:.1f} KB（要求 ≥{min_size/1024}KB）")
    
    return passed, total


def test_modules():
    """测试关键模块可导入"""
    print("\n📦 模块导入检查:")
    
    modules = [
        ("src.crawler.xhs_adapter", "Stage-1: 爬虫"),
        ("src.pipeline.cleaner", "Stage-2: 清洗"),
        ("src.graph.builder", "Stage-3: 图构建"),
        ("src.graph.analytics", "Stage-3: 分析"),
        ("src.graph.visualizer", "Stage-3: 可视化"),
        ("src.app.dashboard", "Stage-4: Dashboard"),
        ("src.utils.packaging", "工具: 打包"),
    ]
    
    passed = 0
    total = len(modules)
    
    for module_name, desc in modules:
        try:
            __import__(module_name)
            print(f"  ✅ {desc:25s} ({module_name})")
            passed += 1
        except ImportError as e:
            print(f"  ❌ {desc:25s} ({module_name}) - {e}")
        except Exception as e:
            print(f"  ⚠️  {desc:25s} ({module_name}) - {e}")
    
    return passed, total


def test_dependencies():
    """测试核心依赖"""
    print("\n🔧 依赖检查:")
    
    deps = [
        "streamlit",
        "networkx",
        "pyvis",
        "scipy",
        "pandas",
        "google.protobuf",
    ]
    
    passed = 0
    total = len(deps)
    
    for dep in deps:
        try:
            mod = __import__(dep.replace(".", "_") if "." in dep else dep)
            version = getattr(mod, "__version__", "unknown")
            print(f"  ✅ {dep:20s} - {version}")
            passed += 1
        except ImportError:
            print(f"  ❌ {dep:20s} - 未安装")
    
    return passed, total


def main():
    """主测试流程"""
    print("=" * 70)
    print("🧪 Smoke Test - 冒烟测试")
    print("=" * 70)
    print("验证 Stage 1-4 核心功能是否正常（回归测试）")
    
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"\n📁 工作目录: {project_root}")
    
    # 执行测试
    results = []
    
    results.append(("数据文件", *test_data_files()))
    results.append(("输出文件", *test_output_files()))
    results.append(("模块导入", *test_modules()))
    results.append(("依赖检查", *test_dependencies()))
    
    # 汇总
    print("\n" + "=" * 70)
    print("📊 测试汇总:")
    
    total_passed = 0
    total_checks = 0
    
    for name, passed, total in results:
        total_passed += passed
        total_checks += total
        status = "✅" if passed == total else "⚠️"
        print(f"  {status} {name:15s}: {passed}/{total} 通过")
    
    # 总体结果
    pass_rate = total_passed / total_checks * 100 if total_checks > 0 else 0
    
    print("=" * 70)
    
    if pass_rate == 100:
        print(f"🎉 所有测试通过！({total_passed}/{total_checks})")
        print("\n✅ 系统完全正常，可以启动 Dashboard")
        print("\n🚀 启动命令:")
        print("  uv run python -m streamlit run src/app/dashboard.py")
        return 0
    
    elif pass_rate >= 70:
        print(f"⚠️  部分测试通过 ({total_passed}/{total_checks}, {pass_rate:.1f}%)")
        print("\n🔧 建议:")
        print("  1. 检查上述失败项")
        print("  2. 运行 'uv run python scripts/doctor.py' 获取详细诊断")
        return 1
    
    else:
        print(f"❌ 测试失败 ({total_passed}/{total_checks}, {pass_rate:.1f}%)")
        print("\n🔧 请先修复以下问题:")
        print("  1. 运行 'uv venv' 创建虚拟环境")
        print("  2. 运行 'uv pip install -r requirements.txt' 安装依赖")
        print("  3. 运行爬虫和清洗脚本生成数据")
        return 2


if __name__ == "__main__":
    sys.exit(main())
