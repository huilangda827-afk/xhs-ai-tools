AI Tools 数据挖掘工作站（XHS Graph Miner）

一个面向“内容创作者”的端到端数据挖掘小工具：从爬取/导入数据 → 清洗治理 → 图谱建模 → 趋势洞察 → 可视化展示 → 文案/素材包生成，提供一套可运行、可演示、可扩展到公网部署的工程化流水线。

适用场景：在信息爆炸的时代，帮助创作者更快“读懂”某个关键词赛道：它和哪些主题强关联、热点关系怎么变化、该怎么选题/拟标题/配标签、如何更快产出可发布内容。

项目亮点

图谱可视化（可交互）：标签共现网络 + 社区聚类，一眼看到关键词周边主题结构与圈层分布

趋势关系（Rising Edges）：关注“最近突然一起出现的标签组合”，而不是只做词频统计

创作者可读的洞察输出：把算法结果翻译成“结论 + 建议”（选题角度、标题结构、话术、标签组合、素材建议）

一键演示 / 一键出包：演示数据可完整跑通流程，支持导出 submission 压缩包

工程化探索：Windows 本地开发 + Docker 容器化 + VPS 部署尝试（公网可访问）

功能总览（Dashboard）

Dashboard 使用 Streamlit 实现，包含三个核心页面：

图谱分析

标签共现图谱（交互式 HTML 图）

PageRank Top 标签榜

Rising Edges 趋势榜（含样本不足自动降级 fallback）

原帖样本

展示清洗后的样本数据（演示/真实数据切换）

生成文案 / 素材包

生成多条草稿（标题/正文/标签/发布建议等）

可扩展：接入 LLM 提升文案质量（当前已预留接口或规划中）

快速开始（本地运行）
1) 创建虚拟环境并安装依赖（推荐 uv）
uv venv
uv pip install -r requirements.txt

2) 环境自检
uv run python scripts/doctor.py

3) 启动 Dashboard
uv run python -m streamlit run src/app/dashboard.py


启动成功后浏览器打开：

http://localhost:8501（或终端提示的端口）

演示模式 vs 真实爬取

本项目支持两种数据源：

Sample Data（演示模式）：仓库内提供少量样本数据，保证无需登录/无需爬虫即可完整演示全流程

Crawled Data（真实数据）：通过 Playwright 模拟浏览器爬取（可能需要登录/验证码/稳定网络/依赖完善）

说明：为了控制仓库体积并避免上传敏感信息，本仓库默认不包含真实抓取的全量数据与浏览器登录态。

Docker / VPS 部署（可选）

项目曾尝试部署到海外 VPS 并通过域名访问（示例：https://lab.redjade.tech/）。
由于服务器资源限制（如 1GB 内存）与依赖差异，部署过程中可能出现：

依赖缺失（如 cache 模块、playwright 依赖）

文件权限问题（如 /app/data/output/graph.html 无写权限）

headless 模式与登录流程适配

如需部署，建议：

使用 docker-compose up -d 启动

确保容器内依赖与数据目录权限正确（chmod -R / 使用非 root 用户策略）

playwright 需要额外安装浏览器：playwright install chromium

仓库内容说明（为什么没有 .venv / 大数据）

为了便于老师下载与复现，本仓库只包含源码与必要的演示数据，不上传以下内容：

.venv/ 虚拟环境（体积巨大、跨平台不可复用）

browser_data/ 登录态（可能含 cookie/敏感信息）

data/raw/ data/clean/ data/output/ 全量产物（可再生、体积大）

如需完整运行真实爬取，请按文档安装依赖并在本地生成数据。

目录结构（简要）
src/                # Streamlit 仪表盘与核心逻辑
scripts/            # 自检、测试、数据处理脚本
media_platform/     # 平台适配层（xhs 等）
proxy/              # 代理与网络相关模块
data/               # 演示样本/运行数据（仓库仅保留 samples）
docs/               # 项目架构与说明文档
docker-compose.yml  # 容器编排（可选）
Dockerfile          # 镜像构建（可选）

使用建议（给验收/演示）

推荐验收路径（无需爬虫）：

启动 Dashboard

选择 Sample Data（演示模式）

点击 Mine（挖掘）

展示：图谱 + PageRank + Rising Edges + 文案生成 + 导出包

致谢 / 工程记录

本项目开发过程中持续迭代：完成一个功能往往会触发新的兼容性与部署问题（依赖、编码、权限、跨平台）。
也探索过云端部署、Docker 化、文件传输等工程实践，并保留了大量调试记录与文档。

License

MIT (or your choice)

如果你愿意，我还可以顺手给你补两样“老师很吃这一套”的内容：

README 里加一个 “截图展示区”（图谱页、文案页、VPS 访问页）占位

加一个 “一键运行（Windows）” 小节（把你现在用过的命令串成 3 行）
