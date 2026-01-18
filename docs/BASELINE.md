# 基线文档 - BASELINE

## 🎯 当前成果（不可回归）

本文档记录了 Stage 1-4 的核心成果，**任何后续改动都不得破坏这些功能**。

---

## ✅ Stage 1：爬虫（XHS Crawler）

### 可运行命令

```bash
uv run python scripts/test_crawl_raw.py
```

### 预期输出

- 文件：`data/raw/annotations.jsonl`
- 数据量：≥ 5 条（可配置）
- 字段完整：item_id, source, url, time, title, desc, text, tags, images

### 验收标准

- [ ] 命令能正常执行（扫码登录一次后可复用）
- [ ] 输出文件存在且格式正确
- [ ] 每条数据包含 9 个必需字段

---

## ✅ Stage 2：数据清洗

### 可运行命令

```bash
python scripts/clean_data_direct.py
```

### 预期输出

- 文件：`data/clean/annotations_clean.jsonl`
- 报告：`data/stats/cleaning_report.json`
- 通过率：≥ 80%

### 验收标准

- [ ] 清洗脚本能正常执行
- [ ] 清洗后数据字段完整
- [ ] 清洗报告包含统计信息（raw_count, clean_count, drop_reasons）

---

## ✅ Stage 3：图谱挖掘

### 核心功能

1. **标签共现图构建**
   - 节点：标签（tag）
   - 边：共现关系
   - 权重：共现频率

2. **PageRank 分析**
   - Top 15 核心标签
   - 基于图结构重要性

3. **Rising Edges 趋势发现**
   - 基于数据内最大时间（anchor_now）
   - 时间窗口：Recent 7天 vs Historical 30天
   - 非空保证：Fallback 到全局 Top Edges

### 可运行命令

```bash
uv run python scripts/test_graph.py
```

### 预期输出

- 文件：`data/output/graph.html`
- 控制台：PageRank Top 列表 + Rising Edges 列表

### 验收标准

- [ ] 图谱 HTML 生成成功（文件大小 > 10KB）
- [ ] PageRank Top 非空（至少 5 个标签）
- [ ] Rising Edges 有输出（真实 rising 或 fallback）
- [ ] 显示窗口样本数（Recent/Historical/Total）

---

## ✅ Stage 4：Streamlit Dashboard

### 启动命令

```bash
uv run python -m streamlit run src/app/dashboard.py
```

### 页面元素（必须存在）

#### 左侧边栏

1. **控制面板**
   - 数据源选择（Crawled Data / Sample Data）
   - Mine 按钮

2. **样例数据管理**
   - 操作模式（仅查看 / 覆盖 / 合并去重）
   - 执行按钮

3. **数据统计**
   - Raw 行数
   - Clean 行数
   - 当前使用行数

4. **导出提交包**
   - 生成 ZIP 按钮
   - 下载按钮

#### 主区域 - Tab 1：图谱分析

1. **标签共现图谱**
   - 交互式网络图（可拖拽、缩放）
   - 节点大小：按 PageRank 缩放
   - 边粗细：按共现次数缩放
   - 下载图谱 HTML 按钮

2. **PageRank Top 榜单**（左侧表格）
   - 15 行数据
   - 列：排名、标签、PageRank 分数

3. **Rising Edges 趋势榜**（右侧表格）
   - 模式标识：Rising 或 Fallback（带警告色）
   - 窗口信息：Anchor Now | Recent | Historical | Total
   - 10 行数据
   - 列：排名、标签组合、增幅/共现次数

#### 主区域 - Tab 2：原帖样本

1. **笔记卡片列表**
   - 可展开/收起
   - 显示：标题、描述、标签、图片数、链接
   - 分页显示（每页 10 条）

#### 底部

1. **系统日志**（可展开）
   - 最近 10 条日志
   - 格式：[时间] 级别: 消息

### 验收标准

- [ ] 页面能正常启动（http://localhost:8501）
- [ ] 所有上述元素存在且可交互
- [ ] Mine 按钮能显示进度条和日志
- [ ] 图谱能正常显示（不空白）
- [ ] PageRank 和 Rising Edges 表格有数据
- [ ] 导出功能能生成并下载 ZIP

---

## 📊 数据文件基线

| 文件路径 | 最小要求 | 说明 |
|---------|---------|------|
| `data/raw/annotations.jsonl` | ≥ 1 行 | 原始爬取数据 |
| `data/clean/annotations_clean.jsonl` | ≥ 1 行 | 清洗后数据 |
| `data/samples/annotations_sample.jsonl` | ≥ 20 行 | 演示样例（兜底）|
| `data/stats/cleaning_report.json` | 存在 | 清洗报告 |
| `data/output/graph.html` | > 10KB | 交互式图谱 |

---

## 🔒 改动约束

### 允许的改动

✅ **新增文件**（不影响现有文件）
✅ **新增 Tab**（不改现有 Tab 布局）
✅ **新增侧边栏区域**（不改现有控件）
✅ **新增 API/模块**（不改现有模块逻辑）

### 禁止的改动

❌ **删除或重命名现有文件**
❌ **修改现有 Tab 的布局/内容**
❌ **改变图谱/PageRank/Rising Edges 的计算逻辑**
❌ **修改数据目录结构**（data/raw, data/clean, data/output）
❌ **引入必须联网/必须 API key 的默认流程**

---

## 🧪 回归测试流程

### 自动化验证

```bash
uv run python scripts/smoke_test.py
```

### 手动验证

1. 启动 Dashboard
2. 选择 Sample Data
3. 点击 Mine
4. 验证：
   - [ ] 图谱显示正常
   - [ ] PageRank Top 有 15 条
   - [ ] Rising Edges 有数据（或 fallback 提示）
   - [ ] 下载按钮可用
   - [ ] 原帖样本可展开

---

## 📝 版本记录

- **基线版本**: v1.0
- **建立时间**: 2026-01-17
- **基线特征**:
  - Stage 1-4 完整可用
  - 图谱可视化正常显示
  - PageRank + Rising Edges 正常工作
  - Dashboard 所有控件可交互

---

**任何后续改动必须确保这些功能不回归！**
