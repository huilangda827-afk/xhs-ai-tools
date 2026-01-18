# -*- coding: utf-8 -*-
"""
XHS Basic Crawler Adapter (Stage-1 稳定版)
最小化包装 MediaCrawler 的小红书爬虫，输出到 data/annotations.jsonl

功能：
- 稳定产出 ≥30 条笔记
- 完整字段：item_id/source/url/time/title/desc/text/tags/images
- 异常处理（不崩溃）
- 追加模式支持
"""
import asyncio
import json
import os
import traceback
from typing import Dict, Optional, Set
from datetime import datetime

from base.base_crawler import AbstractStore
import config
from media_platform.xhs import XiaoHongShuCrawler
from store.xhs import XhsStoreFactory
from tools import utils


class JsonlStoreImplement(AbstractStore):
    """
    自定义 JSONL 存储实现
    
    特性：
    - 写入 data/annotations.jsonl
    - 支持追加模式（不覆盖已有数据）
    - 去重（基于 item_id）
    - 容错处理（字段缺失不崩溃）
    """
    
    # 类变量：跨实例共享的去重集合
    _seen_ids: Set[str] = set()
    _instance_count: int = 0
    
    def __init__(self, output_path: str = "data/raw/annotations.jsonl", append_mode: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.output_path = output_path
        self.item_count = 0
        self.append_mode = append_mode
        
        JsonlStoreImplement._instance_count += 1
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            if self.append_mode:
                # 追加模式：读取已有 item_id 用于去重
                self._load_existing_ids()
                utils.logger.info(f"[JsonlStore] 追加模式，已有 {len(JsonlStoreImplement._seen_ids)} 条数据")
            else:
                # 覆盖模式：清空文件和去重集合
                if JsonlStoreImplement._instance_count == 1:  # 只在第一个实例时清空
                    with open(self.output_path, "w", encoding="utf-8") as f:
                        pass
                    JsonlStoreImplement._seen_ids.clear()
                    utils.logger.info(f"[JsonlStore] 覆盖模式，文件已清空")
            
            utils.logger.info(f"[JsonlStore] 初始化完成，输出: {self.output_path}")
            
        except Exception as e:
            utils.logger.error(f"[JsonlStore] 初始化失败: {e}")
            # 不抛出异常，允许继续运行
    
    def _load_existing_ids(self):
        """加载已存在的 item_id 用于去重"""
        try:
            if os.path.exists(self.output_path):
                with open(self.output_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            item = json.loads(line.strip())
                            if item.get("item_id"):
                                JsonlStoreImplement._seen_ids.add(item["item_id"])
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            utils.logger.warning(f"[JsonlStore] 加载已有数据失败: {e}")
    
    async def store_content(self, content_item: Dict):
        """
        将笔记内容转换为标准 schema 并写入 JSONL
        
        输出字段（严格遵守）：
        - item_id: str - 笔记唯一标识
        - source: str - 固定为 "xhs"
        - url: str|null - 笔记完整URL
        - time: str|null - ISO格式时间
        - title: str - 标题
        - desc: str - 描述
        - text: str - 合并文本（title + desc）
        - tags: list[str] - 标签列表
        - images: list[str] - 图片URL列表
        """
        try:
            # 提取 note_id
            note_id = content_item.get("note_id", "") or ""
            
            # 去重检查
            if note_id in JsonlStoreImplement._seen_ids:
                utils.logger.debug(f"[JsonlStore] 跳过重复: {note_id}")
                return
            
            # 处理 tags：从逗号分隔字符串转为列表
            tags = self._parse_list_field(content_item.get("tag_list", ""))
            
            # 处理 images：从逗号分隔字符串转为列表
            images = self._parse_list_field(content_item.get("image_list", ""))
            
            # 处理时间：转为 ISO 格式
            time_iso = self._parse_time(content_item.get("time"))
            
            # 提取标题和描述
            title = str(content_item.get("title", "") or "").strip()
            desc = str(content_item.get("desc", "") or "").strip()
            
            # 合并文本（用于 NLP 分析）- title + desc
            text = f"{title} {desc}".strip() if title or desc else ""
            
            # 构造标准 schema（9个字段）
            standard_item = {
                "item_id": note_id,
                "source": "xhs",  # 固定值
                "url": content_item.get("note_url") or None,
                "time": time_iso,
                "title": title,
                "desc": desc,
                "text": text,  # title + desc 合并文本
                "tags": tags,
                "images": images
            }
            
            # 写入 JSONL（追加模式）
            with open(self.output_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(standard_item, ensure_ascii=False) + "\n")
            
            # 记录已保存
            JsonlStoreImplement._seen_ids.add(note_id)
            self.item_count += 1
            
            # 简化日志
            utils.logger.info(
                f"[JsonlStore] ✓ #{self.item_count} | {note_id[:8]}... | "
                f"tags:{len(tags)} imgs:{len(images)} | {title[:20]}..."
            )
            
        except Exception as e:
            # 容错：记录错误但不中断
            utils.logger.warning(f"[JsonlStore] 保存失败（已跳过）: {e}")
            utils.logger.debug(traceback.format_exc())
    
    def _parse_list_field(self, value) -> list:
        """解析列表字段（逗号分隔字符串 -> 列表）"""
        try:
            if isinstance(value, list):
                return [str(v).strip() for v in value if v]
            if isinstance(value, str) and value.strip():
                return [v.strip() for v in value.split(",") if v.strip()]
            return []
        except Exception:
            return []
    
    def _parse_time(self, time_value) -> Optional[str]:
        """解析时间字段为 ISO 格式"""
        if not time_value:
            return None
        
        try:
            if isinstance(time_value, (int, float)):
                # 时间戳（秒或毫秒）
                if time_value > 1e12:  # 毫秒级
                    time_value = time_value / 1000
                return datetime.fromtimestamp(time_value).isoformat()
            elif isinstance(time_value, str):
                # 已经是字符串，尝试标准化
                return time_value.strip()
            else:
                return str(time_value)
        except Exception:
            return None
    
    async def store_comment(self, comment_item: Dict):
        """评论数据暂不保存"""
        pass
    
    async def store_creator(self, creator_item: Dict):
        """创作者数据暂不保存"""
        pass
    
    def flush(self):
        """无需 flush（实时写入）"""
        pass
    
    @classmethod
    def get_total_count(cls) -> int:
        """获取已保存的总数"""
        return len(cls._seen_ids)
    
    @classmethod
    def reset(cls):
        """重置类状态（测试用）"""
        cls._seen_ids.clear()
        cls._instance_count = 0


class XhsBasicCrawler:
    """
    XHS 基础爬虫包装器（Stage-1 稳定版）
    
    特性：
    - 复用 MediaCrawler 核心逻辑
    - 自定义存储到 JSONL
    - 稳定的异常处理
    - 支持多关键词
    """
    
    def __init__(
        self, 
        keyword: str = "AI工具", 
        max_notes: int = 40,  # 默认40条，确保有效数据≥30
        append_mode: bool = False
    ):
        """
        Args:
            keyword: 搜索关键词（支持逗号分隔多个）
            max_notes: 最大抓取笔记数（建议40+以确保30+有效数据）
            append_mode: 是否追加模式（True=不清空已有数据）
        """
        self.keyword = keyword
        self.max_notes = max_notes
        self.append_mode = append_mode
        self.output_path = "data/raw/annotations.jsonl"
        
        # 保存原始配置
        self._original_config = {}
    
    async def run(self) -> int:
        """
        运行爬虫，返回成功保存的笔记数
        
        Returns:
            int: 本次保存的笔记数量
        """
        start_count = JsonlStoreImplement.get_total_count()
        
        try:
            # 1. 备份并覆盖配置
            self._backup_config()
            self._override_config()
            
            # 2. 注入自定义存储
            self._inject_custom_store()
            
            # 3. 运行爬虫
            utils.logger.info("=" * 60)
            utils.logger.info(f"[XhsBasicCrawler] 开始爬取")
            utils.logger.info(f"  关键词: {self.keyword}")
            utils.logger.info(f"  目标数量: {self.max_notes}")
            utils.logger.info(f"  追加模式: {self.append_mode}")
            utils.logger.info("=" * 60)
            
            crawler = XiaoHongShuCrawler()
            await crawler.start()
            
            # 4. 统计结果
            end_count = JsonlStoreImplement.get_total_count()
            new_count = end_count - start_count
            
            utils.logger.info("=" * 60)
            utils.logger.info(f"[XhsBasicCrawler] 爬取完成")
            utils.logger.info(f"  本次新增: {new_count} 条")
            utils.logger.info(f"  累计总数: {end_count} 条")
            utils.logger.info(f"  输出文件: {self.output_path}")
            utils.logger.info("=" * 60)
            
            return new_count
            
        except KeyboardInterrupt:
            utils.logger.warning("[XhsBasicCrawler] 用户中断")
            raise
        except Exception as e:
            utils.logger.error(f"[XhsBasicCrawler] 爬取出错: {e}")
            utils.logger.debug(traceback.format_exc())
            # 返回已保存的数量，不抛出异常
            return JsonlStoreImplement.get_total_count() - start_count
        finally:
            # 恢复配置
            self._restore_config()
    
    def _backup_config(self):
        """备份原始配置"""
        self._original_config = {
            "PLATFORM": getattr(config, "PLATFORM", "xhs"),
            "KEYWORDS": getattr(config, "KEYWORDS", ""),
            "CRAWLER_MAX_NOTES_COUNT": getattr(config, "CRAWLER_MAX_NOTES_COUNT", 20),
            "SAVE_DATA_OPTION": getattr(config, "SAVE_DATA_OPTION", "json"),
            "CRAWLER_TYPE": getattr(config, "CRAWLER_TYPE", "search"),
            "ENABLE_GET_COMMENTS": getattr(config, "ENABLE_GET_COMMENTS", True),
            "ENABLE_GET_MEIDAS": getattr(config, "ENABLE_GET_MEIDAS", False),
            "MAX_CONCURRENCY_NUM": getattr(config, "MAX_CONCURRENCY_NUM", 1),
            "SAVE_LOGIN_STATE": getattr(config, "SAVE_LOGIN_STATE", True),
        }
    
    def _override_config(self):
        """覆盖为爬取所需配置"""
        config.PLATFORM = "xhs"
        config.KEYWORDS = self.keyword
        config.CRAWLER_MAX_NOTES_COUNT = self.max_notes
        config.SAVE_DATA_OPTION = "jsonl_custom"
        config.CRAWLER_TYPE = "search"
        
        # 稳定性优化
        config.ENABLE_GET_COMMENTS = False  # 不抓评论（加速）
        config.ENABLE_GET_MEIDAS = False    # 不下载媒体（只存URL）
        config.MAX_CONCURRENCY_NUM = 1      # 串行执行（稳定）
        config.SAVE_LOGIN_STATE = True      # 保存登录态
        
        utils.logger.info("[XhsBasicCrawler] 配置已覆盖")
    
    def _restore_config(self):
        """恢复原始配置"""
        for key, value in self._original_config.items():
            try:
                setattr(config, key, value)
            except Exception:
                pass
        utils.logger.info("[XhsBasicCrawler] 配置已恢复")
    
    def _inject_custom_store(self):
        """注入自定义存储实现"""
        XhsStoreFactory.STORES["jsonl_custom"] = lambda: JsonlStoreImplement(
            output_path=self.output_path,
            append_mode=self.append_mode
        )
        utils.logger.info("[XhsBasicCrawler] 已注入 JSONL 存储")
    
    def get_saved_count(self) -> int:
        """获取已保存的笔记总数"""
        try:
            if not os.path.exists(self.output_path):
                return 0
            with open(self.output_path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
