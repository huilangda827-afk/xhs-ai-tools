# AI Tools 数据挖掘工作站 - 使用指南

## 🎉 Stage 2-4 已完成！

### ✅ 已实现功能

**Stage-2：数据清洗与标准化**
- ✅ 目录结构重组（raw/clean/demo/output/stats）
- ✅ 数据清洗器（`src/pipeline/cleaner.py`）
- ✅ 清洗报告生成（`data/stats/cleaning_report.json`）
- ✅ 20条数据，100%通过率

**Stage-3：图谱挖掘**
- ✅ 标签共现图构建（`src/graph/builder.py`）
- ✅ PageRank 分析（`src/graph/analytics.py`）
- ✅ Rising Edges 趋势发现（时间窗口分析）
- ✅ Pyvis 可视化（`src/graph/visualizer.py`）

**Stage-4：Streamlit 工作站**
- ✅ 单页 Dashboard（`src/app/dashboard.py`）
- ✅ 数据源切换（Crawled / Sample）
- ✅ 一键挖掘功能
- ✅ 图谱+榜单+样本展示

---

## 🚀 快速启动

### 1. 启动 Streamlit Dashboard

```bash
cd D:\multisim\MediaCrawler-main

# 启动工作站
streamlit run src/app/dashboard.py

# 或使用 uv
uv run streamlit run src/app/dashboard.py
```

浏览器会自动打开 `http://localhost:8501`

### 2. 使用流程

1. **选择数据源**
   - Crawled Data：使用真实爬取的20条数据
   - Sample Data：使用演示数据（兜底方案）

2. **点击 Mine 按钮**
   - 等待10-30秒
   - 自动完成图谱构建、PageRank 计算、趋势发现

3. **查看结果**
   - **图谱分析 Tab**：交互式图谱、PageRank Top、Rising Edges
   - **原帖样本 Tab**：数据源内容展示

---

## 📁 文件结构

```
D:\multisim\MediaCrawler-main\
├── src/
│   ├── crawler/
│   │   └── xhs_adapter.py           # Stage-1: 爬虫适配器
│   ├── pipeline/
│   │   └── cleaner.py               # Stage-2: 数据清洗
│   ├── graph/
│   │   ├── builder.py               # Stage-3: 图构建
│   │   ├── analytics.py             # Stage-3: PageRank/趋势
│   │   └── visualizer.py            # Stage-3: 可视化
│   └── app/
│       └── dashboard.py             # Stage-4: Streamlit工作站
├── data/
│   ├── raw/
│   │   └── annotations.jsonl        # 原始数据（20条）
│   ├── clean/
│   │   └── annotations_clean.jsonl  # 清洗后数据（20条）
│   ├── demo/
│   │   └── sample_annotations.jsonl # 演示数据
│   ├── output/
│   │   └── graph.html               # 交互式图谱
│   └── stats/
│       └── cleaning_report.json     # 清洗报告
└── scripts/
    ├── test_crawl_raw.py            # Stage-1: 爬虫测试
    ├── clean_data_direct.py         # Stage-2: 清洗脚本
    └── test_graph.py                # Stage-3: 图谱测试
```

---

## 🔬 核心组件说明

### 1. 数据清洗（`src/pipeline/cleaner.py`）

**清洗规则**：
- 描述长度 ≥ 10 字符
- 标题非空
- 时间非空
- 标签去重、去除 `#` 和 `[话题]` 标记

**运行**：
```bash
python scripts/clean_data_direct.py
```

**输出**：
- `data/clean/annotations_clean.jsonl`
- `data/stats/cleaning_report.json`

---

### 2. 图谱挖掘（`src/graph/`）

**标签共现图**：
- 节点：标签（tag）
- 边：共现关系
- 权重：共现频率

**PageRank**：
- 计算核心话题标签
- Top 15 排名

**Rising Edges**：
- 时间窗口：Recent 7天 vs Historical 30天
- 基准时间：数据内最大时间
- 增长率：`(recent - historical) / (historical + 1)`

**运行**：
```bash
python scripts/test_graph.py
```

---

### 3. Streamlit Dashboard（`src/app/dashboard.py`）

**页面布局**：
- 左侧：控制面板（数据源、Mine按钮、统计信息）
- 右侧：结果展示（Tab1: 图谱分析，Tab2: 原帖样本）

**功能**：
- 数据源切换（兜底演示模式）
- 一键挖掘（30秒内完成）
- 图谱可视化（iframe 内嵌）
- 下载 HTML
- PageRank Top 表格
- Rising Edges 表格（带窗口样本数）

---

## 📊 数据Schema

每条数据包含9个字段：

```json
{
  "item_id": "string",
  "source": "xhs",
  "url": "string|null",
  "time": "ISO-string|null",
  "title": "string",
  "desc": "string",
  "text": "string",
  "tags": ["string", ...],
  "images": ["url", ...]
}
```

---

## 🎯 验收标准

### Stage-2
- [x] `wc -l data/clean/annotations_clean.jsonl` 显示 20 条
- [x] 清洗报告存在且包含统计数据
- [x] 字段完整且 JSON 可解析

### Stage-3
- [x] `data/output/graph.html` 可在浏览器打开并交互
- [x] PageRank Top 榜单非空（15个标签）
- [x] Rising Edges 显示窗口样本数

### Stage-4
- [x] 打开页面后可点击 Mine
- [x] 使用 Sample Data 时 30 秒内出图+榜单
- [x] Crawled Data 模式能正确加载本地数据
- [x] 页面无崩溃，异常有友好提示

---

## 🐛 故障排查

### 问题1：Streamlit 启动失败

**解决**：
```bash
uv pip install streamlit pandas networkx pyvis
```

### 问题2：图谱为空

**原因**：标签数量太少

**解决**：
- 使用 Sample Data 模式
- 或继续爬取更多数据

### 问题3：Rising Edges 为空

**原因**：Recent window 样本数=0

**解决**：这是正常的！Dashboard 会显示"Recent 窗口数据不足"

---

## 📈 后续优化（可选）

### P1 加分项
- [ ] 图片下载到本地
- [ ] 海报生成（Stage-5）
- [ ] 草稿包导出（Stage-5）
- [ ] 多账号内容矩阵（Stage-6）

### 优化方向
- [ ] 增加更多爬取数据（目标 50+ 条）
- [ ] 实时爬取集成（Dashboard 中添加 Crawl 按钮）
- [ ] 标签归一化词典
- [ ] LLM 生成摘要

---

## 🎓 技术栈

- **爬虫**: Playwright + MediaCrawler
- **数据**: JSONL (单一数据源)
- **图挖掘**: NetworkX
- **可视化**: Pyvis
- **Dashboard**: Streamlit
- **依赖管理**: uv

---

## ✅ 交付清单

- [x] `data/clean/annotations_clean.jsonl`（清洗后数据）
- [x] `data/output/graph.html`（可交互图谱）
- [x] `src/app/dashboard.py`（Streamlit 工作站）
- [x] `data/demo/sample_annotations.jsonl`（演示兜底数据）
- [x] `README_USAGE.md`（本文档）
- [x] `data/stats/cleaning_report.json`（清洗报告）

---

**🎉 Stage 2-4 完成！系统已就绪！**

启动命令：`streamlit run src/app/dashboard.py`
