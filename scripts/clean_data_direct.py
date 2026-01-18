# -*- coding: utf-8 -*-
import json
import re
from collections import Counter

# 读取原始数据
raw_items = []
with open("data/raw/annotations.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        raw_items.append(json.loads(line.strip()))

print(f"加载 {len(raw_items)} 条原始数据")

# 清洗
clean_items = []
stats = {"dropped": 0, "reasons": Counter()}

for item in raw_items:
    # 检查必需字段
    if not item.get("title", "").strip():
        stats["dropped"] += 1
        stats["reasons"]["missing_title"] += 1
        continue
    
    if not item.get("time"):
        stats["dropped"] += 1
        stats["reasons"]["missing_time"] += 1
        continue
    
    desc = item.get("desc", "").strip()
    if len(desc) < 10:
        stats["dropped"] += 1
        stats["reasons"]["desc_too_short"] += 1
        continue
    
    # 清洗标签
    raw_tags = item.get("tags", [])
    clean_tags = []
    seen = set()
    
    for tag in raw_tags:
        if not tag:
            continue
        tag = re.sub(r'#', '', str(tag))
        tag = re.sub(r'\[话题\]', '', tag)
        tag = tag.strip()
        
        if tag and len(tag) <= 20 and tag.lower() not in seen:
            clean_tags.append(tag)
            seen.add(tag.lower())
    
    # 保存清洗后的数据
    clean_item = {
        "item_id": item.get("item_id", ""),
        "source": "xhs",
        "url": item.get("url"),
        "time": item.get("time"),
        "title": item.get("title", "").strip(),
        "desc": desc,
        "text": item.get("text", "").strip(),
        "tags": clean_tags,
        "images": item.get("images", [])
    }
    clean_items.append(clean_item)

# 写入清洗后的数据
with open("data/clean/annotations_clean.jsonl", "w", encoding="utf-8") as f:
    for item in clean_items:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

# 生成报告
report = {
    "raw_count": len(raw_items),
    "clean_count": len(clean_items),
    "dropped_count": stats["dropped"],
    "drop_reasons": dict(stats["reasons"]),
    "pass_rate": round(len(clean_items) / len(raw_items) * 100, 2) if raw_items else 0
}

with open("data/stats/cleaning_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"清洗完成: {len(clean_items)} 条")
print(f"丢弃: {stats['dropped']} 条")
print(f"通过率: {report['pass_rate']}%")
