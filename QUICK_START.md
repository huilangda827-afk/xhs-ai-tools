# 🚀 快速启动清单

## 一、核心操作（3步启动）

### 步骤1：抓取数据

```bash
cd D:\multisim\MediaCrawler-main
uv run python scripts/test_crawl_raw.py
```

**说明**：
- 首次运行需扫码登录（120秒内完成）
- 后续运行自动复用登录态
- 默认抓取 5 条，可修改 `scripts/test_crawl_raw.py` 第22行增加数量

**输出**：`data/raw/annotations.jsonl`

---

### 步骤2：清洗数据

```bash
python scripts/clean_data_direct.py
```

**说明**：
- 自动去重、标签清洗、质量过滤
- 生成清洗报告

**输出**：
- `data/clean/annotations_clean.jsonl`
- `data/stats/cleaning_report.json`

---

### 步骤3：启动工作站

```bash
streamlit run src/app/dashboard.py
```

**说明**：
- 浏览器自动打开 `http://localhost:8501`
- 点击左侧 **Mine** 按钮开始挖掘
- 30秒内出图+榜单

**功能**：
- 🕸️ 交互式标签共现图谱
- 🏆 PageRank Top 榜单
- 🔥 Rising Edges 趋势榜
- 📄 原帖样本展示

---

## 二、可能的错误及解决

### ❌ 错误1：`ModuleNotFoundError`

**原因**：依赖未安装

**解决**：
```bash
uv sync
# 或
uv pip install networkx pyvis streamlit pandas
```

---

### ❌ 错误2：扫码登录超时

**原因**：120秒内未完成扫码

**解决**：
1. 确保手机小红书App已登录
2. 扫码要快（60秒内完成）
3. 如果失败，删除缓存重试：
   ```bash
   rmdir /s /q browser_data
   ```

---

### ❌ 错误3：数据文件不存在

**原因**：未运行前置步骤

**解决**：
- 确保先运行步骤1（抓取）
- 再运行步骤2（清洗）
- 最后运行步骤3（工作站）

---

### ❌ 错误4：图谱为空/PageRank为空

**原因**：标签数量太少（<5个）

**解决**：
1. 使用 Sample Data 模式（Dashboard 左侧切换）
2. 或继续抓取更多数据

---

### ❌ 错误5：Rising Edges 为空

**原因**：Recent window 样本数 = 0（正常现象）

**说明**：
- 如果20条数据时间跨度小于7天，可能无历史数据对比
- Dashboard 会显示窗口样本数，这不是错误
- 继续积累数据到50+条即可改善

---

### ❌ 错误6：Streamlit 端口占用

**现象**：提示端口 8501 已被占用

**解决**：
```bash
# 使用其他端口
streamlit run src/app/dashboard.py --server.port 8502
```

---

## 三、数据管理

### 清空所有数据（重新开始）

```bash
# 删除所有数据文件
rmdir /s /q data\raw data\clean data\output data\stats

# 删除浏览器缓存（需重新登录）
rmdir /s /q browser_data

# 重新创建目录
mkdir data\raw data\clean data\demo data\output data\stats
```

---

### 增加数据量

**方法1：修改抓取数量**

编辑 `scripts/test_crawl_raw.py` 第22行：
```python
max_notes = 60  # 改为60（或更多）
```

**方法2：多关键词抓取**

编辑 `scripts/test_crawl_raw.py` 第21行和第23行：
```python
keyword = "DeepSeek"  # 切换关键词
append_mode = True    # 开启追加模式（不覆盖已有数据）
```

依次运行不同关键词：
- AI工具
- DeepSeek
- ChatGPT
- prompt
- AI绘画

每次运行间隔30秒，避免限流。

---

## 四、文件说明

| 文件路径 | 说明 | 何时生成 |
|---------|------|----------|
| `data/raw/annotations.jsonl` | 原始爬取数据 | 步骤1 |
| `data/clean/annotations_clean.jsonl` | 清洗后数据 | 步骤2 |
| `data/stats/cleaning_report.json` | 清洗报告 | 步骤2 |
| `data/output/graph.html` | 交互式图谱 | 步骤3 |
| `data/demo/sample_annotations.jsonl` | 演示数据 | 自动复制 |

---

## 五、验收检查清单

运行以下命令验证：

```bash
# 1. 检查数据文件
dir data\clean\annotations_clean.jsonl

# 2. 统计数据行数
find /c /v "" data\clean\annotations_clean.jsonl

# 3. 验证 JSON 格式
python -c "import json; [json.loads(l) for l in open('data/clean/annotations_clean.jsonl', encoding='utf-8')]"

# 4. 查看清洗报告
type data\stats\cleaning_report.json

# 5. 检查图谱文件
dir data\output\graph.html
```

**预期结果**：
- ✅ 所有文件存在
- ✅ 数据行数 ≥ 15
- ✅ JSON 格式正确
- ✅ 清洗报告包含统计信息
- ✅ graph.html 可在浏览器打开

---

## 六、演示流程（给老师/导师展示）

### 准备阶段（演示前1天）

1. 确保数据量 ≥ 30 条（多运行几次爬虫）
2. 清洗数据
3. 测试 Streamlit 启动

### 演示当天

**方案A（推荐）**：使用 Sample Data 模式
- ✅ 稳定可靠，永不翻车
- ✅ 提前准备好图谱和榜单
- ⚠️ 需说明"这是演示数据"

**方案B**：使用 Crawled Data 模式
- ✅ 真实数据，更有说服力
- ⚠️ 需提前确保网络稳定
- ⚠️ 需备份数据文件

**演示流程**：
1. 打开 Dashboard（提前启动，不当场启动）
2. 介绍数据来源和清洗流程
3. 点击 Mine 展示挖掘过程
4. 解读图谱、PageRank、Rising Edges
5. 展示原帖样本（说明数据质量）

---

## 七、常用命令速查

```bash
# 进入项目目录
cd D:\multisim\MediaCrawler-main

# 爬取数据
uv run python scripts/test_crawl_raw.py

# 清洗数据
python scripts/clean_data_direct.py

# 测试图谱
python scripts/test_graph.py

# 启动工作站
streamlit run src/app/dashboard.py

# 查看数据
type data\clean\annotations_clean.jsonl | more

# 统计行数
find /c /v "" data\clean\annotations_clean.jsonl
```

---

## 🎉 完成标志

看到以下内容说明系统完全就绪：

- [x] 能成功爬取数据（20+ 条）
- [x] 清洗报告通过率 > 80%
- [x] Streamlit 能正常启动
- [x] Mine 按钮能生成图谱和榜单
- [x] 图谱 HTML 可在浏览器打开
- [x] PageRank Top 有结果
- [x] Rising Edges 显示窗口样本数（即使为空）

---

**有问题？查看详细文档 `README_USAGE.md` 或查阅源码注释！** 🚀
