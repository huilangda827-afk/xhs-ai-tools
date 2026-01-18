# -*- coding: utf-8 -*-
"""
Graph Visualizer - Stage 3
图谱可视化：生成交互式 HTML

功能：
- 使用 Pyvis 生成交互式图谱
- 节点大小：按 PageRank 缩放
- 边粗细：按共现次数缩放
- 颜色：按社区检测上色
"""
import os
import networkx as nx
from pyvis.network import Network
from typing import Dict, List, Tuple


class GraphVisualizer:
    """图谱可视化器"""
    
    def __init__(
        self, 
        graph: nx.Graph,
        pagerank_scores: Dict[str, float] = None
    ):
        """
        Args:
            graph: NetworkX 图对象
            pagerank_scores: PageRank 分数字典（可选）
        """
        self.graph = graph
        self.pagerank_scores = pagerank_scores or {}
    
    def create_interactive_html(
        self,
        output_path: str = "data/output/graph.html",
        height: str = "750px",
        width: str = "100%",
        bgcolor: str = "#ffffff",
        font_color: str = "#000000"
    ) -> str:
        """
        生成交互式 HTML 图谱
        
        Args:
            output_path: 输出文件路径
            height: 画布高度
            width: 画布宽度
            bgcolor: 背景色
            font_color: 字体颜色
            
        Returns:
            str: 输出文件路径
        """
        print("=" * 60)
        print("🎨 生成交互式图谱")
        print("=" * 60)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 创建 Pyvis Network
        net = Network(
            height=height,
            width=width,
            bgcolor=bgcolor,
            font_color=font_color,
            notebook=False,
            directed=False
        )
        
        # 配置物理引擎（优化布局）
        net.set_options("""
        {
          "nodes": {
            "font": {"size": 14},
            "borderWidth": 2,
            "shadow": true
          },
          "edges": {
            "color": {"inherit": true},
            "smooth": {"type": "continuous"},
            "shadow": true
          },
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -30000,
              "centralGravity": 0.3,
              "springLength": 95,
              "springConstant": 0.04,
              "damping": 0.09,
              "avoidOverlap": 0.1
            },
            "minVelocity": 0.75,
            "solver": "barnesHut"
          }
        }
        """)
        
        # 社区检测（用于上色）
        communities = self._detect_communities()
        colors = self._generate_colors(len(set(communities.values())))
        
        # 添加节点
        for node in self.graph.nodes():
            # 节点大小：基于 PageRank 或度数
            if self.pagerank_scores and node in self.pagerank_scores:
                size = max(10, self.pagerank_scores[node] * 500)  # 缩放
            else:
                degree = self.graph.degree(node)
                size = max(10, degree * 3)
            
            # 节点颜色：基于社区
            community_id = communities.get(node, 0)
            color = colors[community_id % len(colors)]
            
            # 节点权重（出现次数）
            weight = self.graph.nodes[node].get("weight", 0)
            
            # 添加到 Pyvis
            net.add_node(
                node,
                label=node,
                size=size,
                color=color,
                title=f"<b>{node}</b><br>出现次数: {weight}<br>PageRank: {self.pagerank_scores.get(node, 0):.4f}" if self.pagerank_scores else f"<b>{node}</b><br>出现次数: {weight}",
                mass=size/10  # 影响布局
            )
        
        # 添加边
        for u, v, data in self.graph.edges(data=True):
            weight = data.get("weight", 1)
            
            # 边粗细：基于共现次数
            width = max(1, weight * 0.5)
            
            net.add_edge(
                u, v,
                value=width,
                title=f"共现次数: {weight}"
            )
        
        # 保存
        net.save_graph(output_path)
        
        print(f"✅ 图谱已生成: {output_path}")
        print(f"  节点数: {self.graph.number_of_nodes()}")
        print(f"  边数: {self.graph.number_of_edges()}")
        print(f"  社区数: {len(set(communities.values()))}")
        print("=" * 60)
        
        return output_path
    
    def _detect_communities(self) -> Dict[str, int]:
        """
        社区检测（Louvain 算法）
        
        Returns:
            {node: community_id, ...}
        """
        try:
            import networkx.algorithms.community as nx_comm
            communities = nx_comm.louvain_communities(self.graph, weight="weight")
            
            # 转换为字典
            node_to_community = {}
            for i, community in enumerate(communities):
                for node in community:
                    node_to_community[node] = i
            
            return node_to_community
        except Exception:
            # 如果失败，所有节点分到同一社区
            return {node: 0 for node in self.graph.nodes()}
    
    def _generate_colors(self, n: int) -> List[str]:
        """
        生成颜色列表
        
        Args:
            n: 颜色数量
            
        Returns:
            [color_hex, ...]
        """
        # 预定义调色板
        palette = [
            "#FF6B6B",  # 红
            "#4ECDC4",  # 青
            "#45B7D1",  # 蓝
            "#FFA07A",  # 橙
            "#98D8C8",  # 绿
            "#F7DC6F",  # 黄
            "#BB8FCE",  # 紫
            "#F8B739",  # 金
            "#85C1E2",  # 天蓝
            "#F1948A"   # 粉
        ]
        
        # 如果需要更多颜色，循环使用
        while len(palette) < n:
            palette.extend(palette)
        
        return palette[:n]


def main():
    """测试入口"""
    from src.graph.builder import TagCooccurrenceGraph
    from src.graph.analytics import GraphAnalytics
    
    # 构建图
    print("步骤 1: 构建图...")
    builder = TagCooccurrenceGraph()
    graph = builder.build_graph()
    
    # 分析
    print("\n步骤 2: 计算 PageRank...")
    analytics = GraphAnalytics(graph)
    pagerank_top = analytics.compute_pagerank(top_n=15)
    pagerank_dict = dict(pagerank_top)
    
    # 可视化
    print("\n步骤 3: 生成可视化...")
    visualizer = GraphVisualizer(graph, pagerank_dict)
    output_path = visualizer.create_interactive_html()
    
    print(f"\n🎉 完成！请在浏览器中打开: {output_path}")


if __name__ == "__main__":
    main()
