# -*- coding: utf-8 -*-
"""
Streamlit Dashboard - Stage 4 (Enhanced)
AI Tools 数据挖掘工作站

功能：
- 数据源切换（Crawled / Sample）
- Demo Mode 样例库管理（覆盖/合并去重）
- 一键挖掘（带进度和日志）
- 图谱可视化
- PageRank Top 榜单
- Rising Edges 趋势榜
- 原帖样本展示
- 一键导出提交包
"""
import streamlit as st
import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.graph.builder import TagCooccurrenceGraph
from src.graph.analytics import GraphAnalytics
from src.graph.visualizer import GraphVisualizer
from src.utils.packaging import create_submission_package, deduplicate_jsonl, merge_jsonl_files
from src.app.components.insights import render_insights_panel

# 模板引擎延迟导入（兜底机制，避免新模块拖挂现有功能）
try:
    from src.generator.template_engine import TemplateEngine, save_drafts_package
    TEMPLATE_ENGINE_AVAILABLE = True
    TEMPLATE_ENGINE_ERROR = None
except Exception as e:
    TemplateEngine = None
    save_drafts_package = None
    TEMPLATE_ENGINE_AVAILABLE = False
    TEMPLATE_ENGINE_ERROR = str(e)

# LLM 客户端延迟导入（可选功能，失败不影响模板引擎）
try:
    from src.generator.llm_client import generate_with_llm
    LLM_CLIENT_AVAILABLE = True
except Exception as e:
    generate_with_llm = None
    LLM_CLIENT_AVAILABLE = False


# 页面配置
st.set_page_config(
    page_title="AI Tools 数据挖掘工作站",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 样式
st.markdown("""
<style>
.big-font {
    font-size: 20px !important;
    font-weight: bold;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
</style>
""", unsafe_allow_html=True)

# Session State 初始化（确保所有关键变量都有默认值）
for key, default in {
    "pagerank_top": [],
    "rising_edges": [],
    "window_stats": {},
    "graph_obj": None,
    "graph_path": None,
    "graph_nodes": 0,
    "graph_edges": 0,
    "items": [],
    "logs": [],
    "mine_done": False,
    "generated_drafts": [],
    "trigger_crawl": False,
    "crawl_keyword": "AI工具",
    "crawl_count": 10,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# 标题
st.title("🎯 AI Tools 数据挖掘工作站")
st.markdown("*Stage 1-4 Complete | 从爬取到可视化的完整流程*")
st.markdown("---")


# ============= 辅助函数 =============

def load_jsonl(path):
    """加载 JSONL 文件"""
    items = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                items.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass
    return items


def count_lines(path):
    """统计文件行数"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0


def save_jsonl(items, path):
    """保存 JSONL 文件"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


# ============= 侧边栏：控制面板 =============

with st.sidebar:
    st.header("⚙️ 控制面板")
    
    # === 数据源选择 ===
    st.subheader("📂 数据源")
    data_source = st.radio(
        "选择数据源",
        ["Crawled Data (真实数据)", "Sample Data (演示模式)"],
        help="演示模式使用内置样例，确保稳定"
    )
    
    # 确定数据路径
    if "Sample" in data_source:
        data_path = str(project_root / "data/samples/annotations_sample.jsonl")
        st.caption("💡 使用演示数据（演示永不翻车）")
    else:
        data_path = str(project_root / "data/clean/annotations_clean.jsonl")
        st.caption("💡 使用真实爬取数据")
        
        # === 爬取设置（仅真实数据模式显示）===
        with st.expander("🚀 爬取新数据", expanded=False):
            crawl_keyword = st.text_input(
                "关键词",
                value="AI工具",
                placeholder="输入搜索关键词",
                help="小红书搜索关键词"
            )
            
            crawl_count = st.slider(
                "爬取数量",
                min_value=5,
                max_value=30,
                value=10,
                step=5,
                help="建议 10-20 条，避免触发反爬"
            )
            
            if st.button("🕷️ 开始爬取", use_container_width=True):
                st.session_state.trigger_crawl = True
                st.session_state.crawl_keyword = crawl_keyword
                st.session_state.crawl_count = crawl_count
    
    # === 一键挖掘按钮 ===
    st.markdown("---")
    mine_button = st.button("🔍 Mine（挖掘）", type="primary", use_container_width=True)
    
    if mine_button:
        st.session_state.mining_done = True
        st.session_state.trigger_mine = True
    
    # === Demo Mode 样例库管理 ===
    st.markdown("---")
    st.subheader("📦 样例数据管理")
    
    sample_path = str(project_root / "data/samples/annotations_sample.jsonl")
    raw_path = str(project_root / "data/raw/annotations.jsonl")
    
    demo_action = st.radio(
        "操作模式",
        ["仅查看", "覆盖到 raw", "合并去重到 raw"],
        help="样例数据操作：查看、覆盖或合并"
    )
    
    if st.button("执行样例操作", use_container_width=True):
        try:
            if demo_action == "覆盖到 raw":
                shutil.copy(sample_path, raw_path)
                count = count_lines(raw_path)
                st.success(f"✅ 已覆盖到 raw ({count}条)")
                st.rerun()
            
            elif demo_action == "合并去重到 raw":
                merged_count = merge_jsonl_files([raw_path, sample_path], raw_path)
                st.success(f"✅ 已合并去重 ({merged_count}条)")
                st.rerun()
            
            else:
                sample_items = load_jsonl(sample_path)
                st.info(f"📋 样例数据: {len(sample_items)} 条")
        
        except Exception as e:
            st.error(f"操作失败: {e}")
    
    # === 数据统计 ===
    st.markdown("---")
    st.subheader("📊 数据统计")
    
    raw_count = count_lines(str(project_root / "data/raw/annotations.jsonl"))
    clean_count = count_lines(str(project_root / "data/clean/annotations_clean.jsonl"))
    current_count = count_lines(data_path)
    
    st.metric("Raw 行数", raw_count)
    st.metric("Clean 行数", clean_count)
    st.metric("当前使用", current_count)
    
    with st.expander("📁 文件路径"):
        st.code(f"Raw: {str(project_root / 'data/raw/')}", language="text")
        st.code(f"Clean: {str(project_root / 'data/clean/')}", language="text")
    
    # === 导出提交包 ===
    st.markdown("---")
    st.subheader("📦 导出提交包")
    
    if st.button("🎁 生成 Submission ZIP", use_container_width=True):
        with st.spinner("正在打包..."):
            try:
                zip_path, stats = create_submission_package(
                    output_dir=str(project_root / "data/exports"),
                    project_root=str(project_root)
                )
                
                # 提供下载
                with open(zip_path, "rb") as f:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="📥 下载提交包",
                        data=f.read(),
                        file_name=f"submission_{timestamp}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                
                st.success(f"✅ 包含 {len(stats['files_included'])} 个文件 ({stats['total_size_mb']:.2f} MB)")
            
            except Exception as e:
                st.error(f"打包失败: {e}")


# ============= 主区域 =============

# 初始化 session state
if 'logs' not in st.session_state:
    st.session_state.logs = []

def add_log(msg, level="INFO"):
    """添加日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {msg}"
    st.session_state.logs.append(log_entry)
    if len(st.session_state.logs) > 50:  # 保留最近50条
        st.session_state.logs = st.session_state.logs[-50:]


def fix_html_relative_paths(html_content: str, html_path: str) -> str:
    """
    修复 HTML 中的相对路径，将本地 JS 文件内嵌到 HTML 中
    
    Args:
        html_content: HTML 内容
        html_path: HTML 文件路径（用于解析相对路径）
    
    Returns:
        修复后的 HTML 内容
    """
    import re
    from pathlib import Path
    
    # 获取 HTML 文件所在目录
    html_dir = Path(html_path).parent
    project_root = Path(__file__).parent.parent.parent
    
    # 查找所有相对路径的 script 标签
    pattern = r'<script\s+src=["\']([^"\']+)["\']\s*></script>'
    
    def replace_script(match):
        script_path = match.group(1)
        
        # 只处理相对路径（不以 http:// 或 https:// 开头）
        if script_path.startswith(('http://', 'https://', '//')):
            return match.group(0)  # 保持 CDN 链接不变
        
        # 解析相对路径
        if script_path.startswith('/'):
            # 绝对路径（相对于项目根目录）
            full_path = project_root / script_path.lstrip('/')
        else:
            # 相对路径（相对于 HTML 文件所在目录）
            full_path = html_dir / script_path
        
        # 如果文件存在，读取并内嵌
        if full_path.exists() and full_path.is_file():
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    js_content = f.read()
                # 替换为内嵌 script
                return f'<script>\n{js_content}\n</script>'
            except Exception as e:
                # 如果读取失败，保持原样
                return match.group(0)
        else:
            # 文件不存在，保持原样
            return match.group(0)
    
    # 替换所有匹配的 script 标签
    fixed_html = re.sub(pattern, replace_script, html_content)
    
    return fixed_html


# === 爬取流程（真实数据模式）===

if st.session_state.get("trigger_crawl", False):
    st.session_state.trigger_crawl = False
    
    keyword = st.session_state.get("crawl_keyword", "AI工具")
    count = st.session_state.get("crawl_count", 10)
    
    st.info(f"🕷️ 正在爬取关键词「{keyword}」，目标 {count} 条...")
    st.warning("⚠️ 浏览器将在新窗口打开，请在浏览器中完成登录（如需要）")
    
    progress_bar = st.progress(0, text="启动爬虫子进程...")
    status_text = st.empty()
    
    try:
        import subprocess
        import sys
        import locale
        
        # 使用子进程运行爬虫脚本（避免 Streamlit 环境的 asyncio 冲突）
        crawl_script = str(project_root / "scripts" / "test_crawl_raw.py")
        
        status_text.text("🔄 启动爬虫（新窗口）...")
        progress_bar.progress(20)
        
        # 构建命令
        cmd = [
            sys.executable,
            crawl_script,
            "--keyword", keyword,
            "--count", str(count)
        ]
        
        # Windows 编码修复
        encoding = 'utf-8' if sys.platform != 'win32' else locale.getpreferredencoding(False)
        
        # 运行子进程
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding=encoding,
            errors='replace',  # 遇到无法解码的字符用替代符号
            timeout=300  # 5分钟超时
        )
        
        progress_bar.progress(70)
        
        if result.returncode == 0:
            status_text.text("🔄 清洗数据...")
            
            # 运行清洗
            from src.pipeline.cleaner import DataCleaner
            cleaner = DataCleaner()
            clean_count = cleaner.clean()
            
            progress_bar.progress(100)
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"✅ 爬取完成！清洗后 {clean_count} 条")
            st.info("💡 现在可以点击 **Mine** 按钮分析新数据")
            
            # 显示爬虫输出（添加空值检查）
            with st.expander("📋 爬虫日志", expanded=False):
                stdout = result.stdout or ""
                st.code(stdout[-2000:] if len(stdout) > 2000 else stdout)
            
            # 清除旧数据缓存，强制重新加载
            st.session_state.mining_done = False
            st.session_state.mine_done = False
            st.session_state.items = []  # 清除缓存的数据
            st.session_state.pagerank_top = []
            st.session_state.rising_edges = []
            st.session_state.graph_obj = None
            st.session_state.graph_path = None
            
            # 强制刷新 Dashboard 以显示新数据
            st.rerun()
            
        else:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ 爬取失败（退出码: {result.returncode}）")
            with st.expander("📋 错误详情", expanded=True):
                stderr = result.stderr or ""
                stdout = result.stdout or ""
                st.code(stderr[-2000:] if stderr else stdout[-2000:])
        
    except subprocess.TimeoutExpired:
        progress_bar.empty()
        status_text.empty()
        st.error("❌ 爬取超时（5分钟）")
        st.info("💡 请检查网络或减少爬取数量")
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ 爬取失败: {e}")
        st.info("💡 可能原因：网络问题、登录过期、反爬限制")


# === 挖掘流程 ===

if not st.session_state.get("mining_done", False):
    # 未开始挖掘
    st.info("👈 请在左侧选择数据源，然后点击 **Mine** 按钮开始挖掘")
    
    # 显示说明
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📖 功能说明")
        st.markdown("""
        - **图谱分析**: 标签共现网络可视化
        - **PageRank Top**: 核心话题标签排名
        - **Rising Edges**: 趋势组合发现
        - **原帖样本**: 数据源内容展示
        - **Demo Mode**: 演示兜底（永不翻车）
        - **一键导出**: 提交包生成
        """)
    
    with col2:
        st.subheader("🎓 使用建议")
        st.markdown("""
        1. 首次使用建议选择 **Sample Data**
        2. 点击 **Mine** 后等待 10-30 秒
        3. 可下载图谱 HTML 本地查看
        4. 切换数据源后需重新挖掘
        5. 演示前建议先测试一遍完整流程
        """)

elif st.session_state.get("trigger_mine", False):
    # 开始挖掘
    st.session_state.trigger_mine = False
    
    # 进度显示
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 日志显示
    log_expander = st.expander("📋 详细日志", expanded=True)
    with log_expander:
        log_area = st.empty()
    
    try:
        # === 步骤 1: 加载数据 ===
        status_text.text("🔄 步骤 1/5: 加载数据...")
        progress_bar.progress(0.1)
        add_log("开始加载数据文件")
        
        builder = TagCooccurrenceGraph(data_path)
        items = builder.load_data()
        
        if not items:
            add_log("❌ 数据文件为空或不存在", "ERROR")
            st.error("数据文件为空，请先爬取数据或使用 Sample Data")
            st.session_state.mining_done = False
            st.stop()
        
        add_log(f"✅ 成功加载 {len(items)} 条数据", "SUCCESS")
        log_area.code("\n".join(st.session_state.logs[-10:]))
        
        # === 步骤 2: 构建图谱 ===
        status_text.text("🔄 步骤 2/5: 构建图谱...")
        progress_bar.progress(0.3)
        add_log("开始构建标签共现图")
        log_area.code("\n".join(st.session_state.logs[-10:]))
        
        graph = builder.build_graph()
        
        if graph.number_of_nodes() == 0:
            add_log("❌ 图谱为空（标签数量不足）", "ERROR")
            st.error("标签数量不足，无法构建图谱")
            st.session_state.mining_done = False
            st.stop()
        
        add_log(f"✅ 图谱构建完成: {graph.number_of_nodes()} 节点, {graph.number_of_edges()} 边", "SUCCESS")
        log_area.code("\n".join(st.session_state.logs[-10:]))
        
        # === 步骤 3: 计算 PageRank ===
        status_text.text("🔄 步骤 3/5: 计算 PageRank...")
        progress_bar.progress(0.5)
        add_log("开始 PageRank 计算")
        log_area.code("\n".join(st.session_state.logs[-10:]))
        
        analytics = GraphAnalytics(graph, data_path)
        pagerank_top = analytics.compute_pagerank(top_n=15)
        
        add_log(f"✅ PageRank 完成: Top {len(pagerank_top)} 标签", "SUCCESS")
        log_area.code("\n".join(st.session_state.logs[-10:]))
        
        # === 步骤 4: 发现趋势边 ===
        status_text.text("🔄 步骤 4/5: 发现趋势边...")
        progress_bar.progress(0.7)
        add_log("开始 Rising Edges 分析")
        log_area.code("\n".join(st.session_state.logs[-10:]))
        
        rising_edges, window_stats = analytics.find_rising_edges(
            recent_days=7,
            historical_days=30,
            top_n=10
        )
        
        add_log(f"✅ 趋势分析完成: Recent {window_stats['recent_count']} | Historical {window_stats['historical_count']}", "SUCCESS")
        log_area.code("\n".join(st.session_state.logs[-10:]))
        
        # === 步骤 5: 生成可视化 ===
        status_text.text("🔄 步骤 5/5: 生成可视化...")
        progress_bar.progress(0.9)
        add_log("开始生成交互式图谱")
        log_area.code("\n".join(st.session_state.logs[-10:]))
        
        visualizer = GraphVisualizer(graph, dict(pagerank_top))
        graph_path = str(project_root / "data/output/graph.html")
        visualizer.create_interactive_html(graph_path)
        
        add_log(f"✅ 图谱已生成: {graph_path}", "SUCCESS")
        log_area.code("\n".join(st.session_state.logs[-10:]))
        
        # === 完成 ===
        progress_bar.progress(1.0)
        status_text.text("✅ 挖掘完成！")
        add_log("🎉 所有步骤成功完成", "SUCCESS")
        log_area.code("\n".join(st.session_state.logs[-10:]))
        
        # 保存结果到 session state
        st.session_state.pagerank_top = pagerank_top
        st.session_state.rising_edges = rising_edges
        st.session_state.window_stats = window_stats
        st.session_state.graph_path = graph_path
        st.session_state.items = items
        st.session_state.graph_nodes = graph.number_of_nodes()
        st.session_state.graph_edges = graph.number_of_edges()
        st.session_state.graph_obj = graph  # 保存图对象（用于洞察面板）
        st.session_state.mine_done = True  # 标记挖掘完成
        
        # 清除触发状态，准备显示结果
        st.session_state.trigger_mine = False
        st.session_state.show_results = True  # 标记显示结果
        
        st.success("✅ 挖掘完成！请查看下方结果")
        
        # 强制刷新以显示结果
        st.rerun()
        
    except Exception as e:
        add_log(f"❌ 失败: {str(e)}", "ERROR")
        log_area.code("\n".join(st.session_state.logs[-10:]))
        st.error(f"挖掘失败: {e}")
        st.session_state.mining_done = False
        st.session_state.trigger_mine = False
        progress_bar.progress(0)
        status_text.text("❌ 挖掘失败")
        st.stop()

if st.session_state.get("show_results", False):
    # 显示结果（Mine 成功后）
    st.success("✅ 挖掘完成！")
    
    # Tabs（新增 Generate Tab）
    tab1, tab2, tab3 = st.tabs(["📊 图谱分析", "📝 原帖样本", "✨ 生成文案"])
    
    with tab1:
        # === 洞察与建议面板（新增，放在最上方）===
        # 从 session_state 获取数据（兜底机制）
        graph_obj = st.session_state.get("graph_obj")
        pr_top = st.session_state.get("pagerank_top", [])
        rs_edges = st.session_state.get("rising_edges", [])
        ws_stats = st.session_state.get("window_stats", {})
        
        if graph_obj and pr_top:
            try:
                render_insights_panel(
                    graph=graph_obj,
                    pagerank_top=pr_top,
                    rising_edges=rs_edges,
                    window_stats=ws_stats,
                    keyword="AI工具"
                )
                st.markdown("---")
            except Exception as e:
                st.warning(f"洞察面板加载失败: {e}")
        elif not pr_top:
            st.info("💡 请先点击侧边栏的 **Mine** 按钮生成图谱分析结果")
        
        # === 图谱可视化 ===
        st.subheader("🕸️ 标签共现图谱")
        
        graph_path = st.session_state.get("graph_path")
        
        if not graph_path or not os.path.exists(graph_path):
            st.warning("⚠️ 图谱文件不存在，请先点击 Mine 按钮")
        else:
            try:
                # 读取 HTML 内容
                with open(graph_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                
                if not html_content or len(html_content) < 100:
                    st.error(f"❌ 图谱文件为空或损坏: {graph_path}")
                else:
                    # 修复相对路径问题：内嵌本地 JS 文件
                    html_content = fix_html_relative_paths(html_content, graph_path)
                    
                    # 显示文件信息
                    st.caption(f"📁 图谱文件: {graph_path}")
                    
                    # 内嵌图谱（关键：足够的高度 + 允许滚动）
                    st.components.v1.html(html_content, height=800, scrolling=True)
                    
                    # 下载和查看按钮
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        with open(graph_path, "rb") as f:
                            st.download_button(
                                label="📥 下载图谱 HTML",
                                data=f.read(),
                                file_name="tag_graph.html",
                                mime="text/html",
                                use_container_width=True
                            )
                    with col2:
                        st.info(f"💡 图谱已生成，包含 {st.session_state.get('graph_nodes', 0)} 个节点")
            
            except Exception as e:
                st.error(f"❌ 图谱加载失败: {e}")
                st.code(f"路径: {graph_path}")
                import traceback
                st.code(traceback.format_exc())
        
        st.markdown("---")
        
        # === 两列：PageRank + Rising Edges ===
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 PageRank Top 榜单")
            st.caption("核心话题标签排名（基于图结构重要性）")
            
            pagerank_top = st.session_state.get("pagerank_top", [])
            if pagerank_top:
                import pandas as pd
                df = pd.DataFrame({
                    "排名": list(range(1, len(pagerank_top) + 1)),
                    "标签": [tag for tag, _ in pagerank_top],
                    "PageRank": [f"{score:.4f}" for _, score in pagerank_top]
                })
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("暂无数据")
        
        with col2:
            st.subheader("🔥 Rising Edges 趋势榜")
            
            window_stats = st.session_state.get("window_stats", {})
            rising_edges = st.session_state.get("rising_edges", [])
            
            # 显示诊断信息
            mode = window_stats.get('mode', 'rising')
            anchor_now = window_stats.get('anchor_now', 'N/A')
            
            # 模式标识
            if mode == "fallback":
                st.warning("⚠️ 模式: Fallback (窗口样本不足，显示全局 Top Edges)")
            else:
                st.success("✅ 模式: Rising (基于时间窗口对比)")
            
            # 窗口统计
            st.caption(
                f"Anchor: {anchor_now} | "
                f"Recent: {window_stats.get('recent_count', 0)} | "
                f"Historical: {window_stats.get('historical_count', 0)} | "
                f"Total: {window_stats.get('total_count', 0)}"
            )
            
            if rising_edges:
                import pandas as pd
                
                # 根据模式显示不同列
                if mode == "fallback":
                    df = pd.DataFrame({
                        "排名": list(range(1, len(rising_edges) + 1)),
                        "标签组合": [f"{tag1} ↔ {tag2}" for tag1, tag2, _, _ in rising_edges],
                        "共现次数": [details.get('total_count', 0) for _, _, _, details in rising_edges]
                    })
                else:
                    df = pd.DataFrame({
                        "排名": list(range(1, len(rising_edges) + 1)),
                        "标签组合": [f"{tag1} ↔ {tag2}" for tag1, tag2, _, _ in rising_edges],
                        "增幅": [f"+{details.get('growth_rate', 0)*100:.1f}%" for _, _, _, details in rising_edges],
                        "Recent": [details.get('recent_count', 0) for _, _, _, details in rising_edges],
                        "Historical": [details.get('historical_count', 0) for _, _, _, details in rising_edges]
                    })
                
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("暂无数据")
    
    with tab2:
        st.subheader("📄 原帖样本")
        
        items = st.session_state.get("items", [])
        
        if items:
            # 分页显示
            items_per_page = 10
            total_pages = (len(items) + items_per_page - 1) // items_per_page
            
            page = st.selectbox("页码", range(1, total_pages + 1))
            start_idx = (page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(items))
            
            page_items = items[start_idx:end_idx]
            
            for i, item in enumerate(page_items, start_idx + 1):
                with st.expander(f"📝 笔记 {i}: {item.get('title', '无标题')[:60]}..."):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**标题**: {item.get('title', '')}")
                        desc = item.get('desc', '')
                        st.markdown(f"**描述**: {desc[:300]}{'...' if len(desc) > 300 else ''}")
                        st.markdown(f"**时间**: {item.get('time', '未知')}")
                    
                    with col2:
                        tags = item.get('tags', [])
                        st.markdown(f"**标签** ({len(tags)}):")
                        st.write(", ".join(tags[:6]))
                        if len(tags) > 6:
                            st.caption(f"...还有 {len(tags)-6} 个")
                        
                        st.markdown(f"**图片数**: {len(item.get('images', []))}")
                        
                        if item.get('url'):
                            st.markdown(f"[🔗 查看原文]({item['url']})")
        else:
            st.info("暂无数据")
    
    with tab3:
        st.subheader("✨ 文案/素材包生成")
        st.caption("基于挖掘结果生成创作素材（模板引擎，无需 LLM）")
        
        # 检查是否已挖掘
        pagerank_top = st.session_state.get("pagerank_top", [])
        rising_edges = st.session_state.get("rising_edges", [])
        
        if not pagerank_top:
            st.warning("⚠️ 请先在左侧点击 Mine 完成挖掘")
        else:
            # 生成参数
            col1, col2 = st.columns(2)
            
            with col1:
                gen_keyword = st.text_input(
                    "关键词",
                    value="AI工具",
                    help="文案主题关键词"
                )
                
                gen_count = st.number_input(
                    "生成数量",
                    min_value=1,
                    max_value=20,
                    value=5,
                    help="生成草稿数量"
                )
            
            with col2:
                account_mode = st.radio(
                    "账号模式",
                    ["单账号", "多账号（3个）"],
                    help="分配到不同账号"
                )
                
                image_mode = st.radio(
                    "图片模式",
                    ["No images", "Source images (引用原帖)"],
                    help="素材包是否包含图片"
                )
            
            # LLM 可选增强
            st.markdown("---")
            use_llm = st.checkbox(
                "🤖 Use LLM Enhance（可选）",
                value=False,
                help="使用大模型优化文案（需配置 API Key）"
            )
            
            if use_llm:
                with st.expander("⚙️ LLM 配置", expanded=False):
                    llm_provider = st.selectbox(
                        "Provider",
                        ["DeepSeek", "OpenAI", "通义千问", "文心一言"],
                        help="选择大模型提供商"
                    )
                    
                    llm_api_key = st.text_input(
                        "API Key",
                        type="password",
                        placeholder="sk-...",
                        help="留空则使用模板引擎"
                    )
                    
                    if not llm_api_key:
                        st.warning("⚠️ 未配置 API Key，将使用模板引擎生成")
            
            st.markdown("---")
            
            # 检查模板引擎是否可用
            if not TEMPLATE_ENGINE_AVAILABLE:
                st.error(f"❌ 生成模块未就绪：{TEMPLATE_ENGINE_ERROR}")
                st.info("💡 提示：图谱分析和原帖样本功能仍可正常使用")
                st.stop()
            
            # 生成按钮
            if st.button("🎨 生成文案包", type="primary", use_container_width=True):
                with st.spinner("正在生成文案..."):
                    try:
                        # 准备数据
                        top_tags = [tag for tag, _ in pagerank_top[:10]]
                        top_edges_data = [(t1, t2, 0.0) for t1, t2, _, _ in rising_edges[:10]]
                        
                        # 创建生成器
                        engine = TemplateEngine(top_tags, top_edges_data)
                        
                        # 检查 LLM 配置
                        use_llm_generation = False
                        if use_llm:
                            if llm_api_key and llm_api_key.strip():
                                use_llm_generation = True
                                st.info(f"🤖 使用 {llm_provider} 生成")
                            else:
                                st.warning("⚠️ API Key 未配置，使用模板引擎")
                        
                        # 生成草稿
                        if account_mode == "多账号（3个）":
                            accounts = ["测评号", "教程号", "效率号"]
                        else:
                            accounts = ["主账号"]
                        
                        drafts = []
                        llm_success_count = 0
                        
                        # 如果启用 LLM 且有 API Key
                        if use_llm_generation and LLM_CLIENT_AVAILABLE and generate_with_llm:
                            styles = ["清单型", "对比型", "避坑型", "教程型"]
                            
                            # 获取原帖标题作为参考
                            original_titles = []
                            items = st.session_state.get("items", [])
                            for item in items[:5]:
                                if item.get("title"):
                                    original_titles.append(item["title"])
                            
                            # 尝试用 LLM 生成
                            progress_bar = st.progress(0, text="正在调用 LLM API...")
                            
                            for i in range(gen_count):
                                style = styles[i % len(styles)]
                                progress_bar.progress((i + 1) / gen_count, text=f"LLM 生成中... {i+1}/{gen_count}")
                                
                                try:
                                    llm_result = generate_with_llm(
                                        keyword=gen_keyword,
                                        top_tags=top_tags,
                                        top_edges=[(t1, t2) for t1, t2, _ in top_edges_data],
                                        provider=llm_provider,
                                        api_key=llm_api_key,
                                        style=style,
                                        original_titles=original_titles
                                    )
                                except Exception as llm_err:
                                    st.warning(f"⚠️ LLM 调用异常: {llm_err}")
                                    llm_result = None
                                
                                if llm_result:
                                    llm_result["account"] = accounts[i % len(accounts)]
                                    llm_result["content_style"] = style
                                    drafts.append(llm_result)
                                    llm_success_count += 1
                                else:
                                    # LLM 失败，用模板引擎补充
                                    template_draft = engine.generate_draft(gen_keyword)
                                    template_draft["account"] = accounts[i % len(accounts)]
                                    template_draft["fallback_reason"] = "LLM API 调用失败"
                                    drafts.append(template_draft)
                            
                            progress_bar.empty()
                            
                            if llm_success_count > 0:
                                st.success(f"🤖 LLM 成功生成 {llm_success_count} 条")
                            if llm_success_count < gen_count:
                                st.warning(f"⚠️ {gen_count - llm_success_count} 条使用模板引擎回退")
                        
                        else:
                            # 使用模板引擎生成
                            drafts = engine.generate_batch(
                                keyword=gen_keyword,
                                count=gen_count,
                                accounts=accounts
                            )
                        
                        # 保存到 session state
                        st.session_state.generated_drafts = drafts
                        st.session_state.package_keyword = gen_keyword
                        
                        st.success(f"✅ 已生成 {len(drafts)} 条草稿")
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"生成失败: {e}")
            
            # 显示生成结果
            if st.session_state.get("generated_drafts"):
                drafts = st.session_state.generated_drafts
                
                st.markdown("---")
                st.subheader(f"📝 草稿预览（共 {len(drafts)} 条）")
                
                # 显示前3条预览
                for i, draft in enumerate(drafts[:3], 1):
                    with st.expander(f"草稿 {i}/{len(drafts)}: {draft['title'][:50]}..."):
                        st.markdown(f"**账号**: {draft.get('account', 'N/A')}")
                        st.markdown(f"**标题**: {draft['title']}")
                        st.markdown(f"**正文**:\n\n{draft['body']}")
                        st.markdown(f"**标签**: {', '.join(draft['hashtags'][:6])}")
                        st.markdown(f"**生成方式**: {draft.get('generation_method', 'template')}")
                
                if len(drafts) > 3:
                    st.caption(f"...还有 {len(drafts)-3} 条草稿，下载完整包查看")
                
                # 导出按钮
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📦 保存草稿包", use_container_width=True):
                        if not TEMPLATE_ENGINE_AVAILABLE or save_drafts_package is None:
                            st.error("❌ 生成模块未就绪，无法保存")
                        else:
                            package_path = save_drafts_package(drafts)
                            st.success(f"✅ 已保存到: {package_path}")
                
                with col2:
                    # 打包为 ZIP 并下载
                    if st.button("📥 下载 ZIP", use_container_width=True):
                        import zipfile
                        import tempfile
                        
                        # 创建临时 ZIP
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        zip_buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
                        
                        with zipfile.ZipFile(zip_buffer.name, 'w', zipfile.ZIP_DEFLATED) as zf:
                            # drafts.jsonl
                            drafts_content = "\n".join([json.dumps(d, ensure_ascii=False) for d in drafts])
                            zf.writestr("drafts.jsonl", drafts_content)
                            
                            # README
                            readme = f"""草稿包

关键词: {st.session_state.get('package_keyword', 'N/A')}
生成数量: {len(drafts)}
生成时间: {timestamp}

使用方法：
1. 打开 drafts.jsonl
2. 每行是一条草稿（JSON格式）
3. 可根据 account 字段分配到不同账号

字段说明：
- title: 标题
- body: 正文
- hashtags: 推荐标签
- account: 账号分配
"""
                            zf.writestr("README.txt", readme)
                        
                        with open(zip_buffer.name, "rb") as f:
                            st.download_button(
                                label="💾 下载草稿包",
                                data=f.read(),
                                file_name=f"drafts_{timestamp}.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                        
                        os.unlink(zip_buffer.name)


# === 日志展示（底部）===
with st.expander("📋 系统日志（最近10条）", expanded=False):
    if st.session_state.logs:
        st.code("\n".join(st.session_state.logs[-10:]), language="log")
    else:
        st.info("暂无日志")


# 页脚
st.markdown("---")
st.caption("🎓 AI Tools 数据挖掘工作站 | Powered by MediaCrawler + NetworkX + Streamlit")
