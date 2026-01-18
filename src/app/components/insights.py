# -*- coding: utf-8 -*-
"""
Insights Panel - 洞察与建议面板
基于图谱分析结果生成可读结论（不依赖 LLM）

功能：
- A1: 一句话结论（What's happening）
- A2: 热点结构（So what）
- A3: 创作建议（Now what）
- A4: 可信度提示（Data quality）
- A5: 图例说明（How to read）
"""
import networkx as nx
from typing import List, Tuple, Dict


class InsightsGenerator:
    """洞察生成器"""
    
    def __init__(
        self,
        graph: nx.Graph,
        pagerank_top: List[Tuple[str, float]],
        rising_edges: List[Tuple[str, str, float, dict]],
        window_stats: Dict,
        keyword: str = "AI工具"
    ):
        """
        Args:
            graph: NetworkX 图对象
            pagerank_top: PageRank Top 列表
            rising_edges: Rising Edges 列表
            window_stats: 窗口统计信息
            keyword: 关键词
        """
        self.graph = graph
        self.pagerank_top = pagerank_top
        self.rising_edges = rising_edges
        self.window_stats = window_stats
        self.keyword = keyword
    
    def generate_summary(self) -> str:
        """
        A1: 生成一句话结论
        
        Returns:
            summary: 一句话结论文本
        """
        if not self.pagerank_top:
            return f"【{self.keyword}】的内容分析数据不足。"
        
        # 中心标签（PageRank Top 1）
        center_tag = self.pagerank_top[0][0]
        
        # 子话题（Top 2-4 标签）
        subtopics = [tag for tag, _ in self.pagerank_top[1:4]]
        subtopics_str = "、".join(subtopics) if subtopics else "多个方向"
        
        # Rising/Top 组合
        mode = self.window_stats.get("mode", "rising")
        
        if mode == "fallback" or not self.rising_edges:
            # Fallback 模式
            if self.rising_edges:
                top_combos = [f"{t1}×{t2}" for t1, t2, _, _ in self.rising_edges[:3]]
                combo_str = "、".join(top_combos)
                summary = (
                    f"【{self.keyword}】的内容核心围绕**{center_tag}**，"
                    f"主要分为{subtopics_str}等子话题；"
                    f"常见联动组合包括：{combo_str}。"
                )
            else:
                summary = (
                    f"【{self.keyword}】的内容核心围绕**{center_tag}**，"
                    f"主要分为{subtopics_str}等子话题。"
                )
        else:
            # Rising 模式
            rising_combos = [f"{t1}×{t2}" for t1, t2, _, _ in self.rising_edges[:3]]
            combo_str = "、".join(rising_combos) if rising_combos else "暂无明显趋势"
            summary = (
                f"【{self.keyword}】的内容核心围绕**{center_tag}**，"
                f"主要分为{subtopics_str}等子话题；"
                f"近期更常联动的组合是：{combo_str}。"
            )
        
        return summary
    
    def detect_communities(self, top_k: int = 3) -> List[Dict]:
        """
        A2: 检测并返回 Top K 社区
        
        Args:
            top_k: 返回社区数量
            
        Returns:
            [{'id': 1, 'tags': [...], 'size': N}, ...]
        """
        try:
            import networkx.algorithms.community as nx_comm
            communities = nx_comm.louvain_communities(self.graph, weight="weight")
            
            # 按社区大小排序
            communities_sorted = sorted(communities, key=len, reverse=True)
            
            # 取 Top K
            result = []
            for i, comm in enumerate(communities_sorted[:top_k], 1):
                # 获取社区内标签的 PageRank 排序
                comm_tags = list(comm)
                
                # 如果有 PageRank，按 PageRank 排序
                pagerank_dict = dict(self.pagerank_top)
                comm_tags_sorted = sorted(
                    comm_tags,
                    key=lambda t: pagerank_dict.get(t, 0),
                    reverse=True
                )
                
                result.append({
                    "id": i,
                    "tags": comm_tags_sorted[:5],  # 每个社区取前5个代表标签
                    "size": len(comm_tags)
                })
            
            return result
        
        except Exception:
            # 如果失败，返回空列表
            return []
    
    def generate_creation_suggestions(self) -> List[Dict]:
        """
        A3: 生成创作建议（6条）
        
        Returns:
            [{'type': '选题', 'suggestion': '...'}, ...]
        """
        suggestions = []
        
        # === 选题建议（2条）===
        if self.rising_edges and len(self.rising_edges) >= 2:
            tag1_a, tag1_b, _, _ = self.rising_edges[0]
            suggestions.append({
                "type": "选题",
                "suggestion": f"结合「{tag1_a}」和「{tag1_b}」的对比测评"
            })
            
            if len(self.rising_edges) >= 2:
                tag2_a, tag2_b, _, _ = self.rising_edges[1]
                suggestions.append({
                    "type": "选题",
                    "suggestion": f"围绕「{tag2_a}」和「{tag2_b}」的组合教程"
                })
        else:
            # Fallback
            if self.pagerank_top and len(self.pagerank_top) >= 3:
                tag1 = self.pagerank_top[0][0]
                tag2 = self.pagerank_top[1][0]
                suggestions.append({
                    "type": "选题",
                    "suggestion": f"聚焦「{tag1}」的深度解析"
                })
                suggestions.append({
                    "type": "选题",
                    "suggestion": f"「{tag1}」与「{tag2}」的对比分析"
                })
        
        # === 结构建议（2条）===
        suggestions.append({
            "type": "结构",
            "suggestion": "清单型：N个工具推荐 + 简短点评 + 适用场景"
        })
        suggestions.append({
            "type": "结构",
            "suggestion": "对比型：横向评测 + 优缺点表格 + 选择建议"
        })
        
        # === 标签建议（1条）===
        if self.pagerank_top and len(self.pagerank_top) >= 5:
            main_tag = self.pagerank_top[0][0]
            aux_tags = [tag for tag, _ in self.pagerank_top[1:5]]
            suggestions.append({
                "type": "标签",
                "suggestion": f"主标签「{main_tag}」+ 辅助标签「{aux_tags[0]}、{aux_tags[1]}、{aux_tags[2]}」"
            })
        else:
            suggestions.append({
                "type": "标签",
                "suggestion": f"主标签「{self.keyword}」+ 相关热门标签"
            })
        
        # === 标题建议（1条）===
        if self.pagerank_top:
            top_tag = self.pagerank_top[0][0]
            suggestions.append({
                "type": "标题",
                "suggestion": f"标题公式：N个{top_tag} + 实测/避坑/必备 + 收藏"
            })
        else:
            suggestions.append({
                "type": "标题",
                "suggestion": "标题公式：数字 + 关键词 + 行动词 + 情感词"
            })
        
        return suggestions
    
    def get_data_quality_info(self) -> Dict:
        """
        A4: 获取可信度提示信息
        
        Returns:
            {'total': X, 'anchor': ..., 'mode': ..., 'warning': ...}
        """
        mode = self.window_stats.get("mode", "rising")
        total = self.window_stats.get("total_count", 0)
        recent = self.window_stats.get("recent_count", 0)
        historical = self.window_stats.get("historical_count", 0)
        anchor = self.window_stats.get("anchor_now", "N/A")
        
        warning = None
        if mode == "fallback":
            if recent < 5 and historical < 5:
                warning = f"窗口样本不足（Recent: {recent}, Historical: {historical}），已启用 Fallback 模式"
            elif recent < 5:
                warning = f"Recent 窗口样本不足（{recent}条），趋势分析可靠性降低"
            elif historical < 5:
                warning = f"Historical 窗口样本不足（{historical}条），基线对比有限"
        
        return {
            "total": total,
            "recent": recent,
            "historical": historical,
            "anchor_now": anchor,
            "mode": mode,
            "warning": warning
        }
    
    @staticmethod
    def get_legend() -> Dict:
        """
        A5: 获取图例说明
        
        Returns:
            {'nodes': ..., 'edges': ..., 'colors': ...}
        """
        return {
            "nodes": "节点 = 标签，大小表示 PageRank 重要性",
            "edges": "连线 = 共现关系，粗细表示共现频率",
            "colors": "颜色 = 社区/话题簇（相似标签聚集）",
            "interaction": "💡 可拖拽节点、滚轮缩放、悬停查看详情"
        }


def render_insights_panel(
    graph: nx.Graph,
    pagerank_top: List[Tuple[str, float]],
    rising_edges: List,
    window_stats: Dict,
    keyword: str = "AI工具"
):
    """
    渲染洞察面板（在 Streamlit 中调用）
    
    Args:
        graph: NetworkX 图
        pagerank_top: PageRank Top 列表
        rising_edges: Rising Edges 列表
        window_stats: 窗口统计
        keyword: 关键词
    """
    import streamlit as st
    
    generator = InsightsGenerator(graph, pagerank_top, rising_edges, window_stats, keyword)
    
    # === A1: 一句话结论 ===
    st.markdown("### 💡 核心洞察")
    summary = generator.generate_summary()
    st.info(summary)
    
    # === A2: 热点结构 ===
    with st.expander("📊 热点结构分析", expanded=False):
        communities = generator.detect_communities(top_k=3)
        
        if communities:
            st.markdown("**Top 3 话题社区：**")
            for comm in communities:
                tags_str = "、".join(comm["tags"])
                st.markdown(f"- **社区 {comm['id']}** ({comm['size']}个标签): {tags_str}")
        else:
            st.markdown("*社区检测数据不足*")
    
    # === A3: 创作建议 ===
    st.markdown("### ✨ 创作建议（可直接使用）")
    
    suggestions = generator.generate_creation_suggestions()
    
    # 按类型分组显示
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 选题方向：**")
        for sug in suggestions:
            if sug["type"] == "选题":
                st.markdown(f"- {sug['suggestion']}")
        
        st.markdown("**📋 内容结构：**")
        for sug in suggestions:
            if sug["type"] == "结构":
                st.markdown(f"- {sug['suggestion']}")
    
    with col2:
        st.markdown("**🏷️ 标签策略：**")
        for sug in suggestions:
            if sug["type"] == "标签":
                st.markdown(f"- {sug['suggestion']}")
        
        st.markdown("**✍️ 标题公式：**")
        for sug in suggestions:
            if sug["type"] == "标题":
                st.markdown(f"- {sug['suggestion']}")
    
    # === A4: 可信度提示 ===
    quality_info = generator.get_data_quality_info()
    
    with st.expander("🔍 数据质量说明", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("总样本数", quality_info["total"])
        with col2:
            st.metric("Recent 窗口", quality_info["recent"])
        with col3:
            st.metric("Historical 窗口", quality_info["historical"])
        
        st.caption(f"**基准时间（Anchor Now）**: {quality_info['anchor_now']}")
        st.caption(f"**分析模式**: {quality_info['mode'].upper()}")
        
        if quality_info["warning"]:
            st.warning(f"⚠️ {quality_info['warning']}")
    
    # === A5: 图例说明 ===
    legend = InsightsGenerator.get_legend()
    
    st.markdown("### 📖 图谱使用说明")
    st.markdown(f"- {legend['nodes']}")
    st.markdown(f"- {legend['edges']}")
    st.markdown(f"- {legend['colors']}")
    st.markdown(f"- {legend['interaction']}")
