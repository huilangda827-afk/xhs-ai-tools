# 交付说明文档 - DELIVERY

## 📦 项目交付信息

- **项目名称**: AI Tools 数据挖掘工作站
- **完成阶段**: Stage 1-4（爬虫 → 清洗 → 图谱 → Dashboard）
- **Python 版本**: >= 3.11
- **依赖管理**: uv（推荐）或 pip
- **主要平台**: 小红书（XHS）

---

## 🚀 Windows 一键验收流程（从 0 到启动）

### 前置条件

1. **已安装 Python 3.11+**
   - 验证：`python --version`
   - 建议：使用 Python 3.11（项目依赖基于此版本）

2. **已安装 uv**
   - 验证：`uv --version`
   - 安装：`irm https://astral.sh/uv/install.ps1 | iex`（PowerShell）

---

### 步骤 1：进入项目目录

```bash
cd D:\multisim\MediaCrawler-main
```

**确认**：该目录下有 `pyproject.toml` 和 `uv.lock` 文件

---

### 步骤 2：创建虚拟环境

```bash
uv venv
```

**预期输出**：
```
Using CPython 3.11.x
Creating virtual environment at: .venv
```

---

### 步骤 3：安装依赖

```bash
uv pip install -r requirements.txt
```

**或者**（如果有 `uv.lock`）：

```bash
uv sync
```

**关键依赖**（会自动安装）：
- streamlit
- protobuf
- networkx
- pyvis
- scipy
- pandas

---

### 步骤 4：环境自检

```bash
uv run python scripts/doctor.py
```

**预期输出**：
```
✅ 所有检查通过！
🚀 可以启动 Dashboard:
  uv run python -m streamlit run src/app/dashboard.py
```

**如果有错误**：按照 doctor.py 给出的修复命令执行

---

### 步骤 5：启动 Dashboard

```bash
uv run python -m streamlit run src/app/dashboard.py
```

**关键**：
- ✅ 使用 `uv run` 确保在虚拟环境中运行
- ✅ 使用 `python -m streamlit` 而不是 `streamlit` 命令
- ✅ 避免调用系统/Anaconda 的 streamlit

**预期输出**：
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

浏览器自动打开，显示完整的工作站界面。

---

## ⚠️ 已知问题与修复（Known Issues & Fix）

### A. uv 环境未创建导致无法安装包

**现象**：
```
error: No virtual environment found; run `uv venv`
```

**解决**：
```bash
uv venv
uv pip install -r requirements.txt
```

---

### B. Streamlit 启动时缺 `google.protobuf`

**现象**：
```
ModuleNotFoundError: No module named 'google.protobuf'
```

**原因**：protobuf 依赖未安装

**解决**：
```bash
uv pip install protobuf
```

---

### C. 缺少 `networkx` / `pyvis` / `scipy`

**现象**：
```
ModuleNotFoundError: No module named 'networkx'
```

**解决**：
```bash
uv pip install networkx pyvis scipy
```

---

### D. Streamlit 找到 Anaconda 版本而不是 uv 虚拟环境

**现象**：
```
File "D:\anaconda\Scripts\streamlit-script.py", line 6, in <module>
```

**原因**：直接使用 `streamlit` 命令会调用系统 PATH 中的版本（可能是 Anaconda）

**解决**：
```bash
# ❌ 错误方式
streamlit run src/app/dashboard.py

# ✅ 正确方式
uv run python -m streamlit run src/app/dashboard.py
```

---

### E. 混用多个 Python 环境

**现象**：
- `uv pip install` 成功，但 `python xxx.py` 仍报缺包
- `import streamlit` OK，但 `streamlit run` 失败

**原因**：系统有多个 Python 环境（Anaconda / 系统 Python / uv venv）

**解决**：
```bash
# 1. 验证当前使用的 Python
uv run python -c "import sys; print(sys.executable)"

# 应输出: D:\multisim\MediaCrawler-main\.venv\Scripts\python.exe

# 2. 如果不是，删除重建
rmdir /s /q .venv
uv venv
uv pip install -r requirements.txt
```

---

### F. 依赖安装慢 / 网络超时

**原因**：默认使用国外 PyPI 源

**解决**：使用清华镜像（已在 `pyproject.toml` 中配置）

```bash
# uv 会自动使用 pyproject.toml 中的镜像配置
uv pip install -r requirements.txt
```

---

## 📋 完整依赖清单

### 核心依赖（必需）

```
streamlit>=1.31.0      # Dashboard框架
protobuf>=4.25.0       # streamlit依赖
networkx>=3.0          # 图谱构建
pyvis>=0.3.2           # 图谱可视化
scipy>=1.11.0          # 图谱算法
pandas>=2.0.0          # 数据处理
```

### MediaCrawler 依赖（已有）

```
httpx==0.28.1          # HTTP客户端
playwright==1.45.0     # 浏览器自动化
tenacity==8.2.2        # 重试机制
pydantic==2.5.2        # 数据验证
```

---

## ✅ 验收命令（按顺序执行）

```bash
# 1. 环境自检
uv run python scripts/doctor.py

# 2. 验证依赖
uv run python -c "import streamlit, google.protobuf, networkx, pyvis, scipy; print('✅ All deps OK')"

# 3. 启动 Dashboard
uv run python -m streamlit run src/app/dashboard.py

# 4. 浏览器访问
# http://localhost:8501
```

---

## 📊 系统要求

| 项目 | 要求 | 验证命令 |
|------|------|----------|
| Python | >= 3.11 | `python --version` |
| uv | 最新版 | `uv --version` |
| 磁盘空间 | >= 2GB | - |
| 网络 | 稳定（首次安装） | - |
| 浏览器 | Chrome/Edge | - |

---

## 🎯 快速故障排查

### 问题：doctor.py 报缺包

```bash
uv pip install -r requirements.txt
```

### 问题：Dashboard 启动失败

```bash
# 1. 确认在项目目录
cd D:\multisim\MediaCrawler-main

# 2. 重新安装依赖
uv pip install streamlit protobuf networkx pyvis scipy pandas

# 3. 使用 python -m 启动
uv run python -m streamlit run src/app/dashboard.py
```

### 问题：端口 8501 占用

```bash
# 使用其他端口
uv run python -m streamlit run src/app/dashboard.py --server.port 8502
```

---

## 📞 技术支持

如果遇到问题：

1. 运行 `uv run python scripts/doctor.py` 查看详细诊断
2. 查看 `docs/KNOWN_ISSUES.md` 的已知问题列表
3. 查看 `核心操作与常见错误.md` 的故障排查章节

---

## 🎉 成功标志

启动成功后，浏览器会显示：
- 🎯 标题："AI Tools 数据挖掘工作站"
- 📂 左侧边栏：控制面板、数据统计、导出功能
- 📊 主区域：图谱分析 + 原帖样本 Tab

---

**最后更新**: 2026-01-17
**维护者**: MediaCrawler Team
