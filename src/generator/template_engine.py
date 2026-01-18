# -*- coding: utf-8 -*-
"""
Template Engine - 模板引擎
基于规则的文案生成（不依赖 LLM）

功能：
- 模板化标题生成
- 结构化正文生成
- 标签组合推荐
"""
import random
import json
from typing import List, Dict, Tuple
from datetime import datetime


class TemplateEngine:
    """模板化文案生成器"""
    
    # 标题模板（4套风格，避免重复）
    TITLE_TEMPLATES = {
        "清单型": [
            "{count}个{topic}推荐 | 实测好用必收藏",
            "超全{topic}清单 | {count}款亲测有效",
            "{year}年{topic}榜单 | Top{count}精选",
            "我整理了{count}个{topic}，建议人手一份",
        ],
        "对比型": [
            "{topic}对比测评 | {count}款横向评测结果",
            "{count}个{topic}实测对比 | 优缺点全分析",
            "大横评！{count}款{topic}谁最强？",
            "{topic}选购指南 | {count}款全面对比",
        ],
        "避坑型": [
            "{topic}避坑指南 | 这{count}个雷别踩",
            "别再被坑了！{topic}真实测评",
            "{count}个{topic}的隐藏问题 | 必看",
            "{topic}踩坑实录 | 帮你省下冤枉钱",
        ],
        "教程型": [
            "{topic}从入门到精通 | {count}步上手",
            "零基础学{topic} | {count}个关键技巧",
            "效率翻倍！{topic}实用教程",
            "{topic}速成指南 | {count}分钟学会",
        ]
    }
    
    # 正文模板（三段式，4套风格）
    BODY_TEMPLATES = {
        "清单型": {
            "hook": [
                "还在为找不到好用的{topic}发愁？我整理了这份清单，建议直接收藏！",
                "做了一周功课，终于找到这{count}个{topic}神器，效率直接起飞。",
                "避免踩坑！这{count}个{topic}是我用过最顺手的，推荐给大家。",
            ],
            "main": [
                "📌 精选清单：\n\n{tools_list}\n\n每个都有独特优势，可以按需选择。",
                "🔥 实测推荐：\n\n{tools_list}\n\n这些工具涵盖了{angle}等场景，基本够用了。",
                "⭐ 核心工具：\n\n{tools_list}\n\n都是经过实际验证的，闭眼入不踩坑。",
            ],
            "cta": [
                "你们还在用哪些{topic}？评论区交流一下~",
                "点赞收藏，下次需要直接翻出来用！",
                "关注我，持续分享更多实用工具和教程。",
            ]
        },
        "对比型": {
            "hook": [
                "市面上{topic}那么多，到底选哪个？我做了横向对比测评。",
                "花了3天时间测试{count}款{topic}，结果出乎意料。",
                "别再纠结了！{count}个{topic}实测对比，看完秒懂该选谁。",
            ],
            "main": [
                "📊 对比结果：\n\n{tools_list}\n\n优缺点都给你们列出来了，根据需求选就行。",
                "🔍 横评发现：\n\n{tools_list}\n\n每款都有侧重点，没有完美的只有最适合的。",
                "⚖️ 实测对比：\n\n{tools_list}\n\n价格、功能、易用性都测了，按需选择。",
            ],
            "cta": [
                "你们会选哪一款？评论区说说看法！",
                "有其他想对比的吗？下期安排~",
                "觉得有用就点个赞，让更多人看到！",
            ]
        },
        "避坑型": {
            "hook": [
                "用{topic}踩了不少坑，总结了这些避坑指南，新手必看。",
                "别再被割韭菜了！{topic}的这些坑一定要知道。",
                "血泪教训！使用{topic}前一定要注意这几点。",
            ],
            "main": [
                "⚠️ 重点避坑：\n\n{tools_list}\n\n这些问题我都遇到过，提前了解能省很多事。",
                "🚫 常见误区：\n\n{tools_list}\n\n避开这些坑，少走弯路。",
                "💡 避坑指南：\n\n{tools_list}\n\n都是真实经验，建议收藏。",
            ],
            "cta": [
                "你们还踩过哪些坑？评论区补充！",
                "关注我，避坑经验持续更新。",
                "转发给需要的朋友，帮TA避坑~",
            ]
        },
        "教程型": {
            "hook": [
                "从零开始学{topic}？这份教程带你快速上手。",
                "{topic}新手必看！{count}步从小白到熟练。",
                "手把手教你用{topic}，5分钟学会，效率翻倍。",
            ],
            "main": [
                "📚 上手指南：\n\n{tools_list}\n\n按照这个顺序学，循序渐进不迷茫。",
                "🎓 学习路径：\n\n{tools_list}\n\n每个都配了实操建议，边学边练。",
                "🔧 实战教程：\n\n{tools_list}\n\n从基础到进阶，全都有。",
            ],
            "cta": [
                "学会了吗？评论区打卡！",
                "关注我，后续分享更多教程。",
                "点赞支持，让更多人学到~",
            ]
        }
    }
    
    # 内容角度
    ANGLES = [
        "对比测评", "避坑清单", "上手教程", "效率提升", "工具组合"
    ]
    
    def __init__(self, top_tags: List[str], top_edges: List[Tuple[str, str, float]]):
        """
        Args:
            top_tags: PageRank Top 标签列表
            top_edges: Top 共现边列表
        """
        self.top_tags = top_tags
        self.top_edges = top_edges
    
    def generate_draft(
        self,
        keyword: str = "AI工具",
        num_tools: int = 5,
        use_llm: bool = False
    ) -> Dict:
        """
        生成单条草稿
        
        Args:
            keyword: 关键词
            num_tools: 推荐工具数量
            use_llm: 是否使用 LLM（暂不实现）
            
        Returns:
            draft: {title, body, hashtags, source_tags, ...}
        """
        if use_llm:
            # 预留 LLM 接口
            return self._generate_with_llm(keyword, num_tools)
        else:
            return self._generate_with_template(keyword, num_tools)
    
    def _generate_with_template(self, keyword: str, num_tools: int) -> Dict:
        """基于模板生成（升级版 - 4套风格轮换）"""
        # 随机选择风格（清单/对比/避坑/教程）
        style = random.choice(list(self.TITLE_TEMPLATES.keys()))
        
        # 选择该风格的模板
        title_tpl = random.choice(self.TITLE_TEMPLATES[style])
        hook_tpl = random.choice(self.BODY_TEMPLATES[style]["hook"])
        main_tpl = random.choice(self.BODY_TEMPLATES[style]["main"])
        cta_tpl = random.choice(self.BODY_TEMPLATES[style]["cta"])
        
        # 选择角度
        angle = random.choice(self.ANGLES)
        
        # 生成标题
        title = title_tpl.format(
            count=num_tools,
            topic=keyword,
            year=datetime.now().year
        )
        
        # 生成工具列表（使用 top_tags）
        tools = self.top_tags[:num_tools] if len(self.top_tags) >= num_tools else self.top_tags
        
        # 根据风格调整工具列表格式
        if style == "清单型":
            tools_list = "\n".join([f"{i+1}. **{tool}** - 核心功能简介" for i, tool in enumerate(tools)])
        elif style == "对比型":
            tools_list = "\n".join([f"{i+1}. **{tool}** - 优点 vs 缺点" for i, tool in enumerate(tools)])
        elif style == "避坑型":
            tools_list = "\n".join([f"{i+1}. 关于**{tool}** - 注意事项" for i, tool in enumerate(tools)])
        else:  # 教程型
            tools_list = "\n".join([f"第{i+1}步：学习 **{tool}**" for i, tool in enumerate(tools)])
        
        # 生成正文（三段式）
        hook = hook_tpl.format(topic=keyword, count=num_tools, angle=angle)
        main = main_tpl.format(tools_list=tools_list, angle=angle)
        cta = cta_tpl.format(topic=keyword)
        
        body = f"{hook}\n\n{main}\n\n{cta}"
        
        # 生成标签（从 top_edges 提取）
        hashtags = self._generate_hashtags(keyword, num_tags=8)
        
        return {
            "title": title,
            "body": body,
            "hashtags": hashtags,
            "source_tags": tools,
            "generation_method": "template_v2",
            "content_style": style,
            "keyword": keyword,
            "angle": angle,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_hashtags(self, keyword: str, num_tags: int = 8) -> List[str]:
        """生成推荐标签"""
        tags = [keyword]  # 关键词作为首个标签
        
        # 添加 PageRank Top 标签
        for tag in self.top_tags[:num_tags]:
            if tag not in tags and tag != keyword:
                tags.append(tag)
        
        # 添加边的标签
        for tag1, tag2, _ in self.top_edges[:num_tags]:
            if tag1 not in tags and len(tags) < num_tags:
                tags.append(tag1)
            if tag2 not in tags and len(tags) < num_tags:
                tags.append(tag2)
        
        return tags[:num_tags]
    
    def _generate_with_llm(self, keyword: str, num_tools: int) -> Dict:
        """使用 LLM 生成（预留接口）"""
        # TODO: 接入 DeepSeek/GPT API
        # 暂时返回模板版本
        return self._generate_with_template(keyword, num_tools)
    
    def generate_batch(
        self,
        keyword: str,
        count: int = 5,
        accounts: List[str] = None
    ) -> List[Dict]:
        """
        批量生成草稿
        
        Args:
            keyword: 关键词
            count: 生成数量
            accounts: 账号列表（用于分配）
            
        Returns:
            [draft1, draft2, ...]
        """
        drafts = []
        
        if accounts is None or len(accounts) == 0:
            # 单账号模式
            accounts = ["主账号"]
        
        # 计算每个账号的草稿数
        per_account = count // len(accounts)
        remainder = count % len(accounts)
        
        for i, account in enumerate(accounts):
            account_count = per_account + (1 if i < remainder else 0)
            
            for j in range(account_count):
                draft = self.generate_draft(keyword, num_tools=5)
                draft["account"] = account
                draft["draft_id"] = f"{account}_{j+1}"
                drafts.append(draft)
        
        return drafts


def save_drafts_package(
    drafts: List[Dict],
    output_dir: str = "data/packs",
    package_name: str = None
) -> str:
    """
    保存草稿包
    
    Args:
        drafts: 草稿列表
        output_dir: 输出目录
        package_name: 包名（默认用时间戳）
        
    Returns:
        package_path: 包目录路径
    """
    if package_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"draft_package_{timestamp}"
    
    package_path = os.path.join(output_dir, package_name)
    os.makedirs(package_path, exist_ok=True)
    
    # 1. 保存 drafts.jsonl
    drafts_file = os.path.join(package_path, "drafts.jsonl")
    with open(drafts_file, "w", encoding="utf-8") as f:
        for draft in drafts:
            f.write(json.dumps(draft, ensure_ascii=False) + "\n")
    
    # 2. 生成 README.txt
    readme_content = f"""# 草稿包说明

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
草稿数量: {len(drafts)}
关键词: {drafts[0].get('keyword', 'N/A') if drafts else 'N/A'}

## 文件说明

- drafts.jsonl: 草稿数据（每行一条）
- README.txt: 本文件

## 草稿字段

每条草稿包含：
- title: 标题
- body: 正文
- hashtags: 推荐标签
- source_tags: 来源标签
- account: 账号分配
- generation_method: 生成方式（template/llm）
- timestamp: 生成时间

## 使用建议

1. 打开 drafts.jsonl 查看所有草稿
2. 根据账号定位选择合适的草稿
3. 可二次编辑标题和正文
4. 添加图片后发布

## 注意事项

- 草稿仅供参考，建议根据实际情况调整
- 标签组合基于数据分析，但需结合平台规则
- 建议分批发布，避免集中上传

---
生成器版本: v1.0（模板引擎）
"""
    
    readme_file = os.path.join(package_path, "README.txt")
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"✅ 草稿包已保存: {package_path}")
    print(f"  - drafts.jsonl ({len(drafts)} 条)")
    print(f"  - README.txt")
    
    return package_path
