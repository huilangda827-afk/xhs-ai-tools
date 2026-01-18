# -*- coding: utf-8 -*-
"""
测试 LLM API 调用
用法: uv run python scripts/test_llm.py <你的API_KEY>
"""
import sys
import os

# 添加项目根目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_llm(api_key: str):
    """测试 LLM 调用"""
    print("=" * 60)
    print("🧪 LLM API 测试")
    print("=" * 60)
    
    # 1. 检查 httpx
    print("\n1️⃣ 检查 httpx...")
    try:
        import httpx
        print(f"   ✅ httpx 版本: {httpx.__version__}")
    except ImportError:
        print("   ❌ httpx 未安装")
        return
    
    # 2. 检查网络连接
    print("\n2️⃣ 检查网络连接...")
    try:
        r = httpx.get("https://api.deepseek.com", timeout=10)
        print(f"   ✅ DeepSeek API 可达 (状态码: {r.status_code})")
    except Exception as e:
        print(f"   ❌ 网络错误: {e}")
        return
    
    # 3. 测试 API 调用
    print("\n3️⃣ 测试 API 调用...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "请用一句话介绍你自己"}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
    }
    
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"   ✅ API 调用成功!")
                print(f"   回复: {content}")
            else:
                print(f"   ❌ API 错误: {response.text}")
                
    except Exception as e:
        print(f"   ❌ 调用失败: {e}")
    
    # 4. 测试完整生成流程
    print("\n4️⃣ 测试完整生成流程...")
    try:
        from src.generator.llm_client import generate_with_llm
        
        result = generate_with_llm(
            keyword="AI工具",
            top_tags=["AI工具", "效率", "ChatGPT", "人工智能"],
            top_edges=[("AI工具", "效率"), ("ChatGPT", "人工智能")],
            provider="DeepSeek",
            api_key=api_key,
            style="清单型"
        )
        
        if result:
            print("   ✅ 生成成功!")
            print(f"   标题: {result.get('title', 'N/A')}")
            print(f"   正文长度: {len(result.get('body', ''))}")
            print(f"   标签: {result.get('hashtags', [])}")
        else:
            print("   ❌ 生成失败（返回 None）")
            
    except Exception as e:
        print(f"   ❌ 生成异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: uv run python scripts/test_llm.py <你的API_KEY>")
        print("例如: uv run python scripts/test_llm.py sk-xxxx")
        sys.exit(1)
    
    api_key = sys.argv[1]
    test_llm(api_key)
