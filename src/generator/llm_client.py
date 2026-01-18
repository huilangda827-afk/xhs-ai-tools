# -*- coding: utf-8 -*-
"""
LLM Client - 大模型 API 调用客户端
支持 DeepSeek、OpenAI、通义千问等

特性：
- 兼容 OpenAI 格式
- 调用失败自动回退
- 不影响现有模板引擎功能
"""
import json
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Provider 配置
PROVIDER_CONFIG = {
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo",
    },
    "通义千问": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-turbo",
    },
    "文心一言": {
        "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat",
        "model": "ernie-speed",
    },
}


def build_prompt(
    keyword: str,
    top_tags: List[str],
    top_edges: List[Tuple[str, str]],
    style: str = "清单型",
    original_titles: List[str] = None
) -> str:
    """
    构建 LLM Prompt
    
    Args:
        keyword: 关键词
        top_tags: PageRank Top 标签
        top_edges: Top 共现组合
        style: 内容风格
        original_titles: 原帖标题（可选）
    
    Returns:
        prompt 文本
    """
    tags_str = "、".join(top_tags[:8]) if top_tags else "无"
    edges_str = "、".join([f"{t1}+{t2}" for t1, t2 in top_edges[:5]]) if top_edges else "无"
    titles_str = "\n".join([f"- {t}" for t in original_titles[:3]]) if original_titles else "无"
    
    prompt = f"""你是一位资深的小红书内容创作专家。请根据以下数据洞察，生成一篇高质量的小红书笔记文案。

## 输入数据

**目标关键词**: {keyword}
**热门标签**: {tags_str}
**热门组合**: {edges_str}
**参考标题**: 
{titles_str}

**内容风格**: {style}

## 输出要求

请严格按照以下 JSON 格式输出，不要添加任何其他内容：

```json
{{
  "title": "标题（15-25字，吸引眼球，包含关键词）",
  "body": "正文（150-300字，分段落，有hook+内容+CTA结构）",
  "hashtags": ["标签1", "标签2", "标签3", "标签4", "标签5"]
}}
```

## 注意事项

1. 标题要有数字、符号或疑问，增加点击率
2. 正文要有层次感，使用 emoji 增加可读性
3. 标签要包含主关键词和相关热门标签
4. 语言风格要口语化、亲切，符合小红书调性
5. 只输出 JSON，不要有其他文字"""

    return prompt


def parse_llm_response(response_text: str) -> Optional[Dict]:
    """
    解析 LLM 返回的 JSON
    
    Args:
        response_text: LLM 返回文本
    
    Returns:
        解析后的 dict 或 None
    """
    try:
        # 尝试直接解析
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # 尝试提取 JSON 块
    import re
    json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # 尝试提取 {...}
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    logger.warning(f"无法解析 LLM 返回: {response_text[:200]}...")
    return None


def call_llm_api(
    prompt: str,
    provider: str = "DeepSeek",
    api_key: str = None,
    timeout: int = 30
) -> Optional[str]:
    """
    调用 LLM API
    
    Args:
        prompt: 提示词
        provider: 服务商
        api_key: API Key
        timeout: 超时时间
    
    Returns:
        LLM 返回文本或 None
    """
    if not api_key:
        logger.warning("未提供 API Key")
        return None
    
    config = PROVIDER_CONFIG.get(provider)
    if not config:
        logger.warning(f"不支持的 Provider: {provider}")
        return None
    
    try:
        # 使用 httpx 直接调用（避免强制依赖 openai 包）
        import httpx
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": config["model"],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    except ImportError:
        # 如果没有 httpx，尝试用 openai
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=api_key,
                base_url=config["base_url"]
            )
            
            response = client.chat.completions.create(
                model=config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000,
            )
            
            return response.choices[0].message.content
        
        except ImportError:
            logger.error("需要安装 httpx 或 openai 包")
            return None
    
    except Exception as e:
        logger.error(f"LLM API 调用失败: {e}")
        # 重新抛出异常，让上层知道具体错误
        raise RuntimeError(f"LLM API 调用失败: {e}") from e


def generate_with_llm(
    keyword: str,
    top_tags: List[str],
    top_edges: List[Tuple[str, str]],
    provider: str = "DeepSeek",
    api_key: str = None,
    style: str = "清单型",
    original_titles: List[str] = None
) -> Optional[Dict]:
    """
    使用 LLM 生成文案（完整流程）
    
    Args:
        keyword: 关键词
        top_tags: Top 标签
        top_edges: Top 组合
        provider: 服务商
        api_key: API Key
        style: 内容风格
        original_titles: 参考标题
    
    Returns:
        生成结果 dict 或 None（失败时）
    """
    if not api_key:
        return None
    
    # 构建 Prompt
    prompt = build_prompt(
        keyword=keyword,
        top_tags=top_tags,
        top_edges=top_edges,
        style=style,
        original_titles=original_titles
    )
    
    # 调用 API
    response_text = call_llm_api(
        prompt=prompt,
        provider=provider,
        api_key=api_key
    )
    
    if not response_text:
        return None
    
    # 解析结果
    result = parse_llm_response(response_text)
    
    if result and all(k in result for k in ["title", "body", "hashtags"]):
        result["generation_method"] = "llm"
        result["llm_provider"] = provider
        result["keyword"] = keyword
        return result
    
    return None
