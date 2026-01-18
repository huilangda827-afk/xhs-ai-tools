# 已知问题与解决方案

本文档记录了在 Windows + uv 环境下开发和部署过程中遇到的所有问题及解决方案。

---

## 🔧 环境问题

### 1. uv 环境未创建

**现象**：
```
error: No virtual environment found; run `uv venv`
```

**原因**：首次使用 uv 需要先创建虚拟环境

**解决**：
```bash
cd D:\multisim\MediaCrawler-main
uv venv
```

---

### 2. google.protobuf 缺失

**现象**：
```
ModuleNotFoundError: No module named 'google.protobuf'
```

**原因**：Streamlit 依赖 protobuf，但未自动安装

**解决**：
```bash
uv pip install protobuf
```

---

### 3. 多 Python 环境混用

**现象**：
- `uv pip install streamlit` 成功
- 但 `streamlit run` 仍报找不到模块
- 错误信息显示 `D:\anaconda\Scripts\streamlit-script.py`

**原因**：系统有多个 Python 环境（Anaconda + uv venv），PATH 优先级导致调用了错误的版本

**解决**：
```bash
# ❌ 错误方式（会调用系统 PATH 的 streamlit）
streamlit run src/app/dashboard.py

# ✅ 正确方式（强制使用 uv 虚拟环境）
uv run python -m streamlit run src/app/dashboard.py
```

---

### 4. scipy 缺失导致图谱算法失败

**现象**：
```
ModuleNotFoundError: No module named 'scipy'
```

**原因**：某些图谱布局或社区检测算法依赖 scipy

**解决**：
```bash
uv pip install scipy
```

---

## 📦 依赖安装问题

### 5. matplotlib 编译失败（Windows）

**现象**：
```
error: metadata-generation-failed
× Encountered error while generating package metadata for matplotlib
```

**原因**：matplotlib 3.9.0 需要 C++ 编译器（Visual Studio）

**解决**：
```bash
# 方案1：使用 uv（会自动下载预编译包）
uv pip install matplotlib

# 方案2：安装不指定版本（让 pip 选择预编译版本）
uv pip install matplotlib --no-build-isolation

# 方案3：跳过 matplotlib（如果不用词云功能）
# 编辑 requirements.txt，注释掉 matplotlib 和 wordcloud
```

---

### 6. wordcloud 编译失败

**现象**：类似 matplotlib 的编译错误

**解决**：
```bash
# 使用 uv sync（会优先使用预编译包）
uv sync

# 或跳过（如果不用词云功能）
# 注释 requirements.txt 中的 wordcloud
```

---

## 🌐 网络问题

### 7. PyPI 连接超时

**现象**：
```
WARNING: Retrying after connection broken by 'SSLError'
```

**解决**：
```bash
# 项目已配置清华镜像（pyproject.toml），正常使用即可
uv pip install -r requirements.txt
```

---

### 8. Playwright 浏览器下载失败

**现象**：
```
Error: Download failed: server returned code 400
```

**解决**：
```bash
# 会自动重试备用源，耐心等待即可
uv run playwright install chromium

# 如果多次失败，可能是网络问题，稍后重试
```

---

## 🔐 登录问题

### 9. 小红书登录超时

**现象**：扫码登录120秒后超时

**解决**：
1. 确保手机小红书 App 已登录
2. 扫码要快（60秒内完成）
3. 如果失败，删除缓存重试：
   ```bash
   rmdir /s /q browser_data
   ```

---

### 10. 登录后仍提示未登录

**现象**：登录成功但爬虫仍报认证失败

**解决**：
```bash
# 删除浏览器缓存，重新登录
rmdir /s /q browser_data\cdp_xhs_user_data_dir
```

---

## 📊 数据问题

### 11. 数据文件不存在

**现象**：Dashboard 提示"数据文件为空"

**解决**：
```bash
# 方法1：使用 Sample Data 模式（演示兜底）
# 在 Dashboard 选择 "Sample Data (演示模式)"

# 方法2：重新爬取
uv run python scripts/test_crawl_raw.py
python scripts/clean_data_direct.py
```

---

### 12. 图谱为空 / PageRank 为空

**现象**：Mine 后提示"标签数量不足"

**原因**：数据太少（<5条）或标签太少

**解决**：
- **立即**：切换到 "Sample Data (演示模式)"
- **根本**：继续爬取数据至 30+ 条

---

### 13. Rising Edges 为空

**现象**：趋势榜显示 "暂无明显趋势边"

**说明**：**这不是错误！** 是正常现象

**原因**：
- 数据时间跨度 < 7 天
- 所有数据都在 Recent 窗口内，无历史对比

**Dashboard 会显示**：
- Recent 样本: 20
- Historical 样本: 0
- 这体现了科学严谨性（不造假数据）

---

## 🖥️ Streamlit 问题

### 14. 端口 8501 占用

**现象**：
```
Port 8501 is in use by another program
```

**解决**：
```bash
# 方案1：使用其他端口
uv run python -m streamlit run src/app/dashboard.py --server.port 8502

# 方案2：关闭占用进程
taskkill /F /IM streamlit.exe
```

---

### 15. Dashboard 样式错乱

**现象**：页面布局异常

**解决**：
```bash
# 清除 Streamlit 缓存
uv run streamlit cache clear

# 重新启动
uv run python -m streamlit run src/app/dashboard.py
```

---

## 🔍 诊断工具

### 环境自检

```bash
uv run python scripts/doctor.py
```

输出包括：
- Python 解释器路径（确保在 `.venv` 中）
- 关键依赖安装状态
- 数据文件存在性
- 一键修复命令

---

### 依赖验证

```bash
uv run python -c "
import streamlit
import google.protobuf
import networkx
import pyvis
import scipy
import pandas
print('✅ All critical deps installed')
"
```

---

## 📝 最佳实践

### ✅ 推荐做法

1. **始终使用 `uv run`** - 确保在虚拟环境中运行
2. **使用 `python -m streamlit`** - 避免 PATH 混淆
3. **首次演示用 Sample Data** - 最稳定
4. **定期运行 doctor.py** - 提前发现问题

### ❌ 避免做法

1. 不要直接 `streamlit run`（会调用系统版本）
2. 不要混用 `pip` 和 `uv pip`（导致环境不一致）
3. 不要在非项目根目录运行脚本
4. 不要删除 `.venv` 后不重新安装依赖

---

## 🎯 成功验收标准

运行以下命令全部通过：

```bash
# 1. 环境检查
uv run python scripts/doctor.py
# 输出：✅ 所有检查通过

# 2. 依赖验证
uv run python -c "import streamlit, networkx, pyvis; print('OK')"
# 输出：OK

# 3. Dashboard 启动
uv run python -m streamlit run src/app/dashboard.py
# 浏览器打开 http://localhost:8501

# 4. 功能验证
# 在 Dashboard 中：
# - 选择 Sample Data
# - 点击 Mine
# - 看到图谱 + PageRank Top + Rising Edges（或fallback）
```

---

## 📞 联系方式

如遇到文档未涵盖的问题：

1. 先运行 `uv run python scripts/doctor.py` 诊断
2. 查看 `核心操作与常见错误.md`
3. 检查命令行完整错误信息

---

**文档版本**: v1.0
**最后更新**: 2026-01-17
