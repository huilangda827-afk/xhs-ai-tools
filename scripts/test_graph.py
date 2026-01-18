# -*- coding: utf-8 -*-
"""测试图谱生成"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.graph.builder import TagCooccurrenceGraph
from src.graph.analytics import GraphAnalytics  
from src.graph.visualizer import GraphVisualizer

# 构建图
print("=" * 60)
print("测试图谱生成")
print("=" * 60)

builder = TagCooccurrenceGraph()
graph = builder.build_graph()

# 计算 PageRank
analytics = GraphAnalytics(graph)
pagerank_top = analytics.compute_pagerank(top_n=15)
pagerank_dict = dict(pagerank_top)

# 生成可视化
visualizer = GraphVisualizer(graph, pagerank_dict)
output_path = visualizer.create_interactive_html()

print(f"\n✅ 成功！图谱已生成: {output_path}")
