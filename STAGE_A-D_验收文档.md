# Stage A-D 验收文档

## ✅ 本次改动总结

---

### 🎯 实施的功能

#### Stage A：洞察与建议面板（已完成）

**新增文件**：
- `src/app/components/__init__.py`
- `src/app/components/insights.py`

**修改文件**：
- `src/app/dashboard.py` - 集成洞察面板

**功能**：
- ✅ A1: 一句话结论（基于 PageRank + Rising Edges）
- ✅ A2: 热点结构（Top 3 社区）
- ✅ A3: 创作建议（6条：选题×2、结构×2、标签×1、标题×1）
- ✅ A4: 可信度提示（窗口样本数、模式、警告）
- ✅ A5: 图例说明（如何阅读图谱）

#### Stage B：Rising Edges 修正（已完成）

**修改文件**：
- `src/graph/analytics.py` - 修正算法
- `src/app/dashboard.py` - UI 显示增强

**功能**：
- ✅ Anchor Now 基于 max(note.time)
- ✅ 非空 Fallback 机制
- ✅ UI 显示窗口诊断信息

#### Stage C：模板文案升级（已完成）

**修改文件**：
- `src/generator/template_engine.py`

**功能**：
- ✅ 4套风格（清单型、对比型、避坑型、教程型）
- ✅ 每套3个子模板（hook、main、cta）
- ✅ 多样性保证（同关键词生成不重复）

#### Stage D：LLM 可选增强（已完成）

**修改文件**：
- `src/app/dashboard.py` - Tab 3 新增 LLM 开关

**功能**：
- ✅ LLM 开关（默认关闭）
- ✅ Provider 选择（DeepSeek/OpenAI等）
- ✅ API Key 输入
- ✅ 无 Key 自动回退模板引擎

#### 回归保护（已完成）

**新增文件**：
- `docs/BASELINE.md`
- `scripts/smoke_test.py`

**修改文件**：
- `scripts/doctor.py` - 新增模块检查

---

## 🧪 验收步骤

### 步骤 1：回归测试

```bash
cd D:\multisim\MediaCrawler-main

# 检查所有模块可导入
uv run python scripts/doctor.py
```

**预期**：
```
✅ Stage-1: 爬虫
✅ Stage-2: 清洗
✅ Stage-3: 图构建
✅ Stage-3: 分析
✅ Stage-3: 可视化
✅ Stage-5: 文案生成
✅ 洞察面板
✅ 工具: 打包
```

---

### 步骤 2：冒烟测试

```bash
uv run python scripts/smoke_test.py
```

**预期**：`🎉 所有测试通过！`

---

### 步骤 3：启动 Dashboard

```bash
uv run python -m streamlit run src/app/dashboard.py
```

---

### 步骤 4：功能验收

#### ✅ Tab 1：图谱分析（验证未破坏 + 新增洞察）

1. **选择** Sample Data
2. **点击** Mine
3. **验证洞察面板**（新增，在图谱上方）：
   - [ ] 💡 核心洞察：一句话结论
   - [ ] 📊 热点结构分析：Top 3 社区（可展开）
   - [ ] ✨ 创作建议：6条建议（选题、结构、标签、标题）
   - [ ] 🔍 数据质量说明：窗口样本数、模式、警告（可展开）
   - [ ] 📖 图谱使用说明：4条图例

4. **验证原有功能**（不得破坏）：
   - [ ] 图谱显示正常（交互式网络图）
   - [ ] PageRank Top 15 条
   - [ ] Rising Edges（Fallback 模式，10条）
   - [ ] 下载按钮可用

---

#### ✅ Tab 2：原帖样本（验证未破坏）

- [ ] 笔记卡片正常显示
- [ ] 可展开查看详情
- [ ] 分页功能正常

---

#### ✅ Tab 3：生成文案（验证升级）

1. **设置参数**：
   - 关键词：AI工具
   - 生成数量：5
   - 账号模式：多账号（3个）
   - 图片模式：No images
   - LLM Enhance：关闭（默认）

2. **点击生成**：
   - [ ] 成功生成 5 条草稿
   - [ ] 草稿风格多样（清单型/对比型/避坑型/教程型）
   - [ ] 每条草稿结构完整（hook + main + cta）
   - [ ] 标签合理（8个）
   - [ ] 账号分配正确（测评号/教程号/效率号）

3. **验证 LLM 开关**（可选）：
   - [ ] 勾选 "Use LLM Enhance"
   - [ ] 显示配置面板（Provider、API Key）
   - [ ] 不填 Key 时提示"将使用模板引擎"
   - [ ] 生成仍然成功（使用模板）

4. **下载功能**：
   - [ ] 📦 保存草稿包
   - [ ] 📥 下载 ZIP
   - [ ] 解压查看（drafts.jsonl + README.txt）

---

## 📊 预期效果

### 洞察面板示例

```
💡 核心洞察
【AI工具】的内容核心围绕AI工具，主要分为ai、ai工具、人工智能等子话题；
常见联动组合包括：AI工具×人工智能、AI工具×ai、ai×ai工具。

✨ 创作建议（可直接使用）

📝 选题方向：
- 结合「AI工具」和「人工智能」的对比测评
- 围绕「AI工具」和「ai」的组合教程

📋 内容结构：
- 清单型：N个工具推荐 + 简短点评 + 适用场景
- 对比型：横向评测 + 优缺点表格 + 选择建议

🏷️ 标签策略：
- 主标签「AI工具」+ 辅助标签「ai、ai工具、人工智能」

✍️ 标题公式：
- 标题公式：N个AI工具 + 实测/避坑/必备 + 收藏
```

### 生成文案示例

```
标题：5个AI工具推荐 | 实测好用必收藏
风格：清单型

正文：
还在为找不到好用的AI工具发愁？我整理了这份清单，建议直接收藏！

📌 精选清单：

1. **AI工具** - 核心功能简介
2. **ai** - 核心功能简介
3. **ai工具** - 核心功能简介
4. **人工智能** - 核心功能简介
5. **AI** - 核心功能简介

每个都有独特优势，可以按需选择。

点赞收藏，下次需要直接翻出来用！

标签：#AI工具 #ai #ai工具 #人工智能 #AI #ChatGPT...
账号：测评号
```

---

## 🔄 回滚方式

如果新功能有问题，需要回滚到之前的版本：

### 方法 1：删除新增文件

```bash
# 删除洞察面板
rmdir /s /q src\app\components

# 恢复 dashboard.py（需要手动或用版本控制）
git checkout src/app/dashboard.py

# 恢复 template_engine.py
git checkout src/generator/template_engine.py
```

### 方法 2：使用备份

```bash
# 如果提前备份了
copy src\app\dashboard.py.bak src\app\dashboard.py
```

---

## ✅ 验收标准

### 必须全部通过

- [ ] `uv run python scripts/doctor.py` - 所有模块检查通过
- [ ] `uv run python scripts/smoke_test.py` - 所有测试通过
- [ ] Dashboard 正常启动
- [ ] Tab 1 显示洞察面板（5个子功能）
- [ ] Tab 1 原有功能不受影响（图谱、PageRank、Rising Edges）
- [ ] Tab 2 原帖样本正常
- [ ] Tab 3 生成文案多样化（4种风格）
- [ ] Tab 3 LLM 开关可用（默认关闭，无 Key 正常运行）

---

## 📝 变更文件列表

### 新增

1. `src/app/components/__init__.py`
2. `src/app/components/insights.py`
3. `docs/BASELINE.md`
4. `scripts/smoke_test.py`
5. `scripts/restart_dashboard.bat`
6. `STAGE_A-D_验收文档.md`（本文件）

### 修改

1. `src/app/dashboard.py` - 集成洞察面板 + LLM 开关
2. `src/graph/analytics.py` - Rising Edges 修正
3. `src/generator/template_engine.py` - 4套风格模板
4. `scripts/doctor.py` - 新增模块检查
5. `requirements.txt` - 补齐依赖

---

## 🎯 立即验收

**运行以下命令**：

```bash
cd D:\multisim\MediaCrawler-main

# 1. 模块检查
uv run python scripts/doctor.py

# 2. 回归测试
uv run python scripts/smoke_test.py

# 3. 启动 Dashboard
uv run python -m streamlit run src/app/dashboard.py
```

**在 Dashboard 中验证**：
1. Tab 1 有洞察面板
2. Tab 3 生成文案风格多样
3. LLM 开关可用（默认关闭正常）

---

**验收完成后告诉我结果！** ✅🚀
