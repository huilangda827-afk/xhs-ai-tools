# -*- coding: utf-8 -*-
"""
XHS 基础爬虫测试脚本

用途：快速验证能否从小红书抓取数据并写入 data/annotations.jsonl

运行方式：
    python scripts/test_crawl_raw.py
    python scripts/test_crawl_raw.py --keyword "星露谷" --count 10
"""
import argparse
import asyncio
import json
import os
import sys
import io

# 修复 Windows 终端编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.crawler.xhs_adapter import XhsBasicCrawler


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="XHS 爬虫测试脚本")
    parser.add_argument("--keyword", "-k", type=str, default="AI工具", help="搜索关键词")
    parser.add_argument("--count", "-c", type=int, default=5, help="爬取数量")
    return parser.parse_args()


async def main():
    """主测试流程"""
    args = parse_args()
    
    print("=" * 60)
    print("🚀 XHS 基础爬虫测试")
    print("=" * 60)
    print()
    
    # 配置（支持命令行参数）
    keyword = args.keyword
    max_notes = args.count
    output_file = "data/raw/annotations.jsonl"
    
    print(f"📌 搜索关键词: {keyword}")
    print(f"📌 目标数量: {max_notes} 条笔记")
    print(f"📌 输出文件: {output_file}")
    print()
    print("⏳ 开始爬取（首次运行可能需要扫码登录）...")
    print("-" * 60)
    print()
    
    try:
        # 创建并运行爬虫
        crawler = XhsBasicCrawler(keyword=keyword, max_notes=max_notes)
        count = await crawler.run()
        
        print()
        print("=" * 60)
        print(f"✅ 爬取完成！成功保存 {count} 条笔记")
        print(f"📄 输出文件: {output_file}")
        print("=" * 60)
        print()
        
        # 显示预览
        if count > 0:
            print("📋 数据预览（前 2 条）:")
            print("-" * 60)
            with open(output_file, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i >= 2:  # 只显示前 2 条
                        break
                    
                    item = json.loads(line)
                    title = item.get("title", "无标题")
                    desc = item.get("desc", "")
                    tags = item.get("tags", [])
                    images = item.get("images", [])
                    time_str = item.get("time", "未知时间")
                    
                    print(f"\n[笔记 {i+1}]")
                    print(f"  标题: {title[:50]}{'...' if len(title) > 50 else ''}")
                    print(f"  描述: {desc[:60]}{'...' if len(desc) > 60 else ''}")
                    print(f"  标签: {tags[:5]}")  # 最多显示 5 个标签
                    print(f"  图片数: {len(images)}")
                    print(f"  时间: {time_str}")
            print()
        
        # 验证 schema
        print("🔍 Schema 验证:")
        print("-" * 60)
        with open(output_file, "r", encoding="utf-8") as f:
            first_item = json.loads(f.readline())
            required_fields = ["item_id", "source", "url", "time", "title", "desc", "tags", "images"]
            
            for field in required_fields:
                value = first_item.get(field)
                status = "✓" if field in first_item else "✗"
                print(f"  {status} {field}: {type(value).__name__}")
        print()
        
        print("=" * 60)
        print("🎉 测试成功！数据已按标准 schema 保存")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 错误: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
