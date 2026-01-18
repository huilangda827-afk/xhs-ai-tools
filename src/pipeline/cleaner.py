# -*- coding: utf-8 -*-
"""
Data Cleaner - Stage 2
数据清洗模块：标准化、去重、质量过滤

功能：
- 清洗标签（去空、去重、移除标记）
- 过滤低质量笔记（描述太短、缺失字段）
- 生成清洗报告
"""
import json
import os
import re
from typing import Dict, List, Tuple
from collections import Counter


class DataCleaner:
    """数据清洗器"""
    
    def __init__(
        self,
        input_path: str = "data/raw/annotations.jsonl",
        output_path: str = "data/clean/annotations_clean.jsonl",
        report_path: str = "data/stats/cleaning_report.json"
    ):
        self.input_path = input_path
        self.output_path = output_path
        self.report_path = report_path
        
        # 清洗统计
        self.stats = {
            "raw_count": 0,
            "clean_count": 0,
            "dropped_count": 0,
            "drop_reasons": Counter(),
            "tag_stats": {
                "before_clean": 0,
                "after_clean": 0,
                "duplicates_removed": 0
            }
        }
    
    def clean(self) -> int:
        """
        执行清洗流程
        
        Returns:
            int: 清洗后的数据条数
        """
        print("=" * 60)
        print("🧹 开始数据清洗")
        print("=" * 60)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
        
        # 读取原始数据
        raw_items = self._load_raw_data()
        self.stats["raw_count"] = len(raw_items)
        print(f"📥 加载原始数据: {self.stats['raw_count']} 条")
        
        # 清洗数据
        clean_items = []
        for item in raw_items:
            clean_item, passed, reason = self._clean_item(item)
            if passed:
                clean_items.append(clean_item)
            else:
                self.stats["dropped_count"] += 1
                self.stats["drop_reasons"][reason] += 1
        
        self.stats["clean_count"] = len(clean_items)
        
        # 保存清洗后的数据
        self._save_clean_data(clean_items)
        
        # 生成报告
        self._generate_report()
        
        print("=" * 60)
        print(f"✅ 清洗完成")
        print(f"  原始: {self.stats['raw_count']} 条")
        print(f"  通过: {self.stats['clean_count']} 条")
        print(f"  丢弃: {self.stats['dropped_count']} 条")
        print(f"  报告: {self.report_path}")
        print("=" * 60)
        
        return self.stats["clean_count"]
    
    def _load_raw_data(self) -> List[Dict]:
        """加载原始数据"""
        items = []
        try:
            with open(self.input_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        items.append(json.loads(line.strip()))
                    except json.JSONDecodeError as e:
                        print(f"⚠️  跳过无效JSON行: {e}")
        except FileNotFoundError:
            print(f"❌ 文件不存在: {self.input_path}")
            return []
        
        return items
    
    def _clean_item(self, item: Dict) -> Tuple[Dict, bool, str]:
        """
        清洗单条数据
        
        Returns:
            (clean_item, passed, drop_reason)
        """
        # 必选字段检查
        if not item.get("title", "").strip():
            return None, False, "missing_title"
        
        if not item.get("time"):
            return None, False, "missing_time"
        
        # 描述长度检查（至少10个字符）
        desc = item.get("desc", "").strip()
        if len(desc) < 10:
            return None, False, "desc_too_short"
        
        # 清洗标签
        raw_tags = item.get("tags", [])
        clean_tags = self._clean_tags(raw_tags)
        
        # 更新标签统计
        self.stats["tag_stats"]["before_clean"] += len(raw_tags)
        self.stats["tag_stats"]["after_clean"] += len(clean_tags)
        self.stats["tag_stats"]["duplicates_removed"] += (len(raw_tags) - len(clean_tags))
        
        # 构造清洗后的数据
        clean_item = {
            "item_id": item.get("item_id", ""),
            "source": item.get("source", "xhs"),
            "url": item.get("url"),
            "time": item.get("time"),
            "title": item.get("title", "").strip(),
            "desc": desc,
            "text": item.get("text", "").strip(),
            "tags": clean_tags,
            "images": item.get("images", [])
        }
        
        return clean_item, True, None
    
    def _clean_tags(self, tags: List[str]) -> List[str]:
        """
        清洗标签列表
        
        规则：
        1. 去除空字符串
        2. 移除 # 和 [话题] 标记
        3. 去重
        4. 去除过长标签（>20字符）
        """
        if not tags:
            return []
        
        cleaned = []
        seen = set()
        
        for tag in tags:
            if not tag or not isinstance(tag, str):
                continue
            
            # 移除 # 和 [话题] 等标记
            tag = re.sub(r'#', '', tag)
            tag = re.sub(r'\[话题\]', '', tag)
            tag = tag.strip()
            
            # 过滤
            if not tag:
                continue
            if len(tag) > 20:  # 过长
                continue
            if tag.lower() in seen:  # 去重（忽略大小写）
                continue
            
            cleaned.append(tag)
            seen.add(tag.lower())
        
        return cleaned
    
    def _save_clean_data(self, items: List[Dict]):
        """保存清洗后的数据"""
        with open(self.output_path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        print(f"💾 清洗数据已保存: {self.output_path}")
    
    def _generate_report(self):
        """生成清洗报告"""
        report = {
            "raw_count": self.stats["raw_count"],
            "clean_count": self.stats["clean_count"],
            "dropped_count": self.stats["dropped_count"],
            "drop_reasons": dict(self.stats["drop_reasons"]),
            "tag_stats": self.stats["tag_stats"],
            "pass_rate": round(self.stats["clean_count"] / self.stats["raw_count"] * 100, 2) if self.stats["raw_count"] > 0 else 0
        }
        
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📊 清洗报告已生成: {self.report_path}")


def main():
    """命令行入口"""
    cleaner = DataCleaner()
    clean_count = cleaner.clean()
    
    if clean_count > 0:
        print(f"\n✅ 成功清洗 {clean_count} 条数据")
    else:
        print(f"\n❌ 清洗失败，请检查输入文件")
    
    return clean_count


if __name__ == "__main__":
    main()
