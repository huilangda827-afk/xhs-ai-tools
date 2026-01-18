# -*- coding: utf-8 -*-
"""
Graph Analytics - Stage 3
图谱分析：PageRank + Rising Edges

功能：
- PageRank 核心标签排名
- Rising Edges 趋势边发现
- 时间窗口分析
"""
import json
import networkx as nx
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter
from itertools import combinations


class GraphAnalytics:
    """图谱分析器"""
    
    def __init__(self, graph: nx.Graph = None, data_path: str = "data/clean/annotations_clean.jsonl"):
        """
        Args:
            graph: NetworkX 图对象（可选）
            data_path: 数据文件路径
        """
        self.graph = graph
        self.data_path = data_path
        self.items = []
    
    def load_data(self):
        """加载数据"""
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.items = [json.loads(line.strip()) for line in f]
        except FileNotFoundError:
            print(f"❌ 文件不存在: {self.data_path}")
            self.items = []
    
    def compute_pagerank(self, top_n: int = 15) -> List[Tuple[str, float]]:
        """
        计算 PageRank 分数
        
        Args:
            top_n: 返回 Top N 标签
            
        Returns:
            [(tag, pagerank_score), ...]
        """
        if not self.graph or not self.graph.nodes:
            print("⚠️  图为空，无法计算 PageRank")
            return []
        
        print("📊 计算 PageRank...")
        
        # 计算 PageRank（考虑边权重）
        pagerank_scores = nx.pagerank(self.graph, weight="weight")
        
        # 排序
        ranked = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
        
        print(f"✅ PageRank Top {top_n}:")
        for i, (tag, score) in enumerate(ranked[:top_n], 1):
            print(f"  {i}. {tag}: {score:.4f}")
        
        return ranked[:top_n]
    
    def find_rising_edges(
        self,
        recent_days: int = 7,
        historical_days: int = 30,
        top_n: int = 10
    ) -> Tuple[List[Tuple[str, str, float, dict]], Dict]:
        """
        发现趋势边（Rising Edges）- 增强版
        
        特性：
        - 基于数据内最大时间（而非 datetime.now()）
        - 非空保证：数据不足时 fallback 到全局 Top Edges
        - 返回详细诊断信息
        
        Args:
            recent_days: 最近窗口（天）
            historical_days: 历史窗口（天）
            top_n: 返回 Top N 趋势边
            
        Returns:
            (edges, window_stats)
            edges: [(tag1, tag2, score, details), ...]
            window_stats: {'anchor_now': ..., 'mode': 'rising'|'fallback', ...}
        """
        if not self.items:
            self.load_data()
        
        print("=" * 60)
        print("🔥 发现趋势边（Rising Edges - Enhanced）")
        print("=" * 60)
        
        # 解析时间并找到最大时间（基准时间 anchor_now）
        items_with_time = []
        for item in self.items:
            time_str = item.get("time")
            if not time_str:
                continue
            
            try:
                # 支持多种时间格式
                time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00').replace(' ', 'T'))
                items_with_time.append((item, time_obj))
            except Exception:
                continue
        
        # 非空 fallback：如果无有效时间数据，返回全局 Top Edges
        if not items_with_time:
            print("⚠️  无有效时间数据，使用 Fallback: Top Co-occurrence Edges")
            return self._fallback_top_edges(top_n)
        
        # 基准时间：数据中的最大时间（anchor_now）
        anchor_now = max(t for _, t in items_with_time)
        recent_threshold = anchor_now - timedelta(days=recent_days)
        historical_threshold = anchor_now - timedelta(days=recent_days + historical_days)
        
        print(f"📅 Anchor Now (数据最大时间): {anchor_now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Recent window: [{recent_threshold.strftime('%Y-%m-%d')} ~ {anchor_now.strftime('%Y-%m-%d')}]")
        print(f"  Historical window: [{historical_threshold.strftime('%Y-%m-%d')} ~ {recent_threshold.strftime('%Y-%m-%d')}]")
        
        # 分窗口统计边权重
        recent_edges = Counter()
        historical_edges = Counter()
        recent_items = []
        historical_items = []
        all_edges = Counter()  # 全局边（用于 fallback）
        
        for item, time_obj in items_with_time:
            tags = item.get("tags", [])
            if len(tags) < 2:
                continue
            
            # 生成标签对
            tag_pairs = list(combinations(sorted(tags), 2))
            
            # 全局统计（fallback 用）
            for pair in tag_pairs:
                all_edges[pair] += 1
            
            # 时间窗口分类
            if time_obj >= recent_threshold:
                for pair in tag_pairs:
                    recent_edges[pair] += 1
                recent_items.append(item)
            elif time_obj >= historical_threshold:
                for pair in tag_pairs:
                    historical_edges[pair] += 1
                historical_items.append(item)
        
        window_stats = {
            "anchor_now": anchor_now.strftime('%Y-%m-%d %H:%M:%S'),
            "recent_count": len(recent_items),
            "historical_count": len(historical_items),
            "total_count": len(items_with_time),
            "recent_edges_count": len(recent_edges),
            "historical_edges_count": len(historical_edges),
            "mode": "rising"  # 默认模式
        }
        
        print(f"  Recent 样本数: {window_stats['recent_count']}")
        print(f"  Historical 样本数: {window_stats['historical_count']}")
        
        # 非空保证：如果任一窗口样本 < 5，使用 fallback
        if window_stats["recent_count"] < 5 or window_stats["historical_count"] < 5:
            print(f"⚠️  窗口样本不足（Recent: {window_stats['recent_count']}, Historical: {window_stats['historical_count']}）")
            print("  使用 Fallback: Top Co-occurrence Edges")
            window_stats["mode"] = "fallback"
            return self._fallback_top_edges(top_n, all_edges, window_stats)
        
        # 计算 Rising Edges
        rising_edges = []
        for edge in set(list(recent_edges.keys()) + list(historical_edges.keys())):
            recent_weight = recent_edges.get(edge, 0)
            historical_weight = historical_edges.get(edge, 0)
            
            # 增长率计算
            growth = (recent_weight - historical_weight) / (historical_weight + 1)
            
            # 只保留有增长的边
            if growth > 0 and recent_weight >= 2:
                details = {
                    "recent_count": recent_weight,
                    "historical_count": historical_weight,
                    "growth_rate": growth
                }
                rising_edges.append((edge[0], edge[1], growth, details))
        
        # 排序
        rising_edges.sort(key=lambda x: x[2], reverse=True)
        
        # 非空保证：如果没有 rising edges，fallback
        if not rising_edges:
            print("  无明显增长边，使用 Fallback: Top Co-occurrence Edges")
            window_stats["mode"] = "fallback"
            return self._fallback_top_edges(top_n, all_edges, window_stats)
        
        print(f"\n🔥 Top {top_n} Rising Edges:")
        for i, (tag1, tag2, growth, details) in enumerate(rising_edges[:top_n], 1):
            print(f"  {i}. {tag1} ↔ {tag2}: +{growth*100:.1f}% (R:{details['recent_count']} H:{details['historical_count']})")
        
        print("=" * 60)
        
        return rising_edges[:top_n], window_stats
    
    def _fallback_top_edges(
        self, 
        top_n: int,
        all_edges: Counter = None,
        window_stats: dict = None
    ) -> Tuple[List[Tuple[str, str, float, dict]], Dict]:
        """
        Fallback: 返回全局共现频率最高的边
        
        Args:
            top_n: 返回数量
            all_edges: 全局边统计（可选）
            window_stats: 窗口统计（可选）
            
        Returns:
            (edges, stats)
        """
        if all_edges is None:
            # 重新统计全局边
            all_edges = Counter()
            for item in self.items:
                tags = item.get("tags", [])
                if len(tags) >= 2:
                    for pair in combinations(sorted(tags), 2):
                        all_edges[pair] += 1
        
        # 转换为统一格式
        top_edges = []
        for (tag1, tag2), count in all_edges.most_common(top_n):
            details = {
                "total_count": count,
                "fallback_reason": "insufficient_window_samples"
            }
            top_edges.append((tag1, tag2, 0.0, details))  # growth=0.0 表示 fallback
        
        if window_stats is None:
            window_stats = {
                "anchor_now": "N/A",
                "recent_count": 0,
                "historical_count": 0,
                "total_count": len(self.items),
                "mode": "fallback"
            }
        
        print(f"\n📊 Fallback: Top {top_n} Co-occurrence Edges:")
        for i, (tag1, tag2, _, details) in enumerate(top_edges[:top_n], 1):
            print(f"  {i}. {tag1} ↔ {tag2}: 共现 {details['total_count']} 次")
        
        return top_edges, window_stats


def main():
    """测试入口"""
    from src.graph.builder import TagCooccurrenceGraph
    
    # 构建图
    builder = TagCooccurrenceGraph()
    graph = builder.build_graph()
    
    # 分析
    analytics = GraphAnalytics(graph)
    
    # PageRank
    pagerank_top = analytics.compute_pagerank(top_n=10)
    
    # Rising Edges
    rising_edges, stats = analytics.find_rising_edges(
        recent_days=7,
        historical_days=30,
        top_n=10
    )


if __name__ == "__main__":
    main()
