#!/usr/bin/env python3
"""
简单 AI 测试 - 验证 V-API 配置
"""
import sys
import asyncio
sys.path.insert(0, '.')

async def test_simple_vapi():
    """简单测试 V-API"""
    import litellm
    from app.config import settings
    
    print("="*70)
    print("简单 V-API 测试")
    print("="*70)
    
    # 配置 V-API
    api_base = f"{settings.VAPI_BASE_URL}/v1"
    api_key = settings.VAPI_API_KEY
    
    print(f"\nV-API 配置:")
    print(f"  Base URL: {api_base}")
    print(f"  API Key: {api_key[:20]}...")
    
    # 测试消息
    messages = [{"role": "user", "content": "你好，请用一句话介绍人工智能"}]
    
    print(f"\n发送测试请求...")
    
    try:
        # 使用 openai 前缀
        response = await litellm.acompletion(
            model="openai/deepseek-chat",
            messages=messages,
            api_base=api_base,
            api_key=api_key,
            temperature=0.3,
            max_tokens=100,
        )
        
        reply = response.choices[0].message.content
        print(f"\n回复：{reply}")
        print(f"\nToken 使用:")
        print(f"  输入：{response.usage.prompt_tokens}")
        print(f"  输出：{response.usage.completion_tokens}")
        print(f"  总计：{response.usage.total_tokens}")
        
        print("\n[SUCCESS] V-API 测试成功!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] V-API 测试失败：{e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_simple_vapi())
    sys.exit(0 if result else 1)
