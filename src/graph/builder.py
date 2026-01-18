# -*- coding: utf-8 -*-
"""
Graph Builder - Stage 3
标签共现图构建器

功能：
- 基于标签共现构建无向图
- 节点：标签（tag）
- 边：共现关系
- 权重：共现频率
"""
import json
import networkx as nx
from typing import List, Dict, Tuple
from itertools import combinations
from collections import Counter


class TagCooccurrenceGraph:
    """标签共现图构建器"""
    
    def __init__(self, data_path: str = "data/clean/annotations_clean.jsonl"):
        """
        Args:
            data_path: 清洗后的数据文件路径
        """
        self.data_path = data_path
        self.graph = nx.Graph()
        self.items = []
        
        # 统计信息
        self.stats = {
            "total_items": 0,
            "total_tags": 0,
            "total_edges": 0,
            "avg_tags_per_item": 0.0
        }
    
    def load_data(self) -> List[Dict]:
        """加载清洗后的数据"""
        items = []
        
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                for line in f:
                    items.append(json.loads(line.strip()))
        except FileNotFoundError:
            print(f"❌ 文件不存在: {self.data_path}")
            return []
        
        self.items = items
        self.stats["total_items"] = len(items)
        
        # 统计标签数
        tag_counts = [len(item.get("tags", [])) for item in items]
        self.stats["avg_tags_per_item"] = sum(tag_counts) / len(tag_counts) if tag_counts else 0
        
        print(f"📥 加载数据: {len(items)} 条笔记")
        print(f"📊 平均标签数: {self.stats['avg_tags_per_item']:.2f}")
        
        return items
    
    def build_graph(self) -> nx.Graph:
        """
        构建标签共现图
        
        Returns:
            networkx.Graph: 构建好的图
        """
        print("=" * 60)
        print("🕸️  开始构建标签共现图")
        print("=" * 60)
        
        if not self.items:
            self.load_data()
        
        # 统计边权重（共现次数）
        edge_weights = Counter()
        node_occurrences = Counter()
        
        for item in self.items:
            tags = item.get("tags", [])
            if not tags or len(tags) < 2:
                continue
            
            # 统计节点出现次数
            for tag in tags:
                node_occurrences[tag] += 1
            
            # 生成标签对（共现边）
            for tag1, tag2 in combinations(sorted(tags), 2):
                edge_weights[(tag1, tag2)] += 1
        
        # 添加节点
        for tag, count in node_occurrences.items():
            self.graph.add_node(tag, weight=count)
        
        # 添加边
        for (tag1, tag2), weight in edge_weights.items():
            self.graph.add_edge(tag1, tag2, weight=weight)
        
        # 更新统计
        self.stats["total_tags"] = self.graph.number_of_nodes()
        self.stats["total_edges"] = self.graph.number_of_edges()
        
        print(f"✅ 图构建完成")
        print(f"  节点数（标签）: {self.stats['total_tags']}")
        print(f"  边数（共现关系）: {self.stats['total_edges']}")
        print("=" * 60)
        
        return self.graph
    
    def get_top_nodes(self, n: int = 10) -> List[Tuple[str, int]]:
        """
        获取出现频率最高的标签
        
        Args:
            n: 返回数量
            
        Returns:
            [(tag, frequency), ...]
        """
        if not self.graph.nodes:
            return []
        
        node_weights = [(node, data.get("weight", 0)) 
                        for node, data in self.graph.nodes(data=True)]
        node_weights.sort(key=lambda x: x[1], reverse=True)
        
        return node_weights[:n]
    
    def get_top_edges(self, n: int = 10) -> List[Tuple[str, str, int]]:
        """
        获取共现频率最高的标签对
        
        Args:
            n: 返回数量
            
        Returns:
            [(tag1, tag2, weight), ...]
        """
        if not self.graph.edges:
            return []
        
        edges_with_weights = [(u, v, data.get("weight", 0)) 
                              for u, v, data in self.graph.edges(data=True)]
        edges_with_weights.sort(key=lambda x: x[2], reverse=True)
        
        return edges_with_weights[:n]
    
    def get_graph_stats(self) -> Dict:
        """获取图的统计信息"""
        if not self.graph:
            return self.stats
        
        # 计算连通分量
        num_components = nx.number_connected_components(self.graph)
        
        # 计算平均度
        degrees = [deg for node, deg in self.graph.degree()]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        
        self.stats.update({
            "num_components": num_components,
            "avg_degree": avg_degree,
            "density": nx.density(self.graph)
        })
        
        return self.stats
    
    def save_graph(self, output_path: str = "data/output/tag_graph.gexf"):
        """
        保存图到文件
        
        Args:
            output_path: 输出文件路径
        """
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        nx.write_gexf(self.graph, output_path)
        print(f"💾 图已保存: {output_path}")


def main():
    """测试入口"""
    builder = TagCooccurrenceGraph()
    graph = builder.build_graph()
    
    print("\n📊 Top 10 标签:")
    for tag, freq in builder.get_top_nodes(10):
        print(f"  {tag}: {freq}")
    
    print("\n🔗 Top 10 共现标签对:")
    for tag1, tag2, weight in builder.get_top_edges(10):
        print(f"  {tag1} ↔ {tag2}: {weight}")
    
    print(f"\n📈 图统计: {builder.get_graph_stats()}")
    
    builder.save_graph()


if __name__ == "__main__":
    main()
