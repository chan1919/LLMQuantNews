#!/usr/bin/env python3
"""
AI 配置测试脚本
测试 V-API 和其他 AI 服务的连通性
"""
import sys
import asyncio
sys.path.insert(0, '.')

from app.config import settings
from app.llm.engine import llm_engine
from app.llm.vapi_service import vapi_service

async def test_vapi_connection():
    """测试 V-API 连接"""
    print("="*70)
    print("测试 V-API 连接")
    print("="*70)
    
    try:
        # 获取模型列表
        print("\n获取 V-API 模型列表...")
        models = await vapi_service.get_chat_models(refresh=True)
        
        if models:
            print(f"[OK] V-API 连接成功！")
            print(f"  可用模型数量：{len(models)}")
            print(f"\n前 5 个模型:")
            for model in models[:5]:
                model_id = model.get('id', 'unknown')
                owned_by = model.get('owned_by', 'unknown')
                print(f"  - {model_id} (by {owned_by})")
            
            return True
        else:
            print("[FAIL] V-API 返回空模型列表")
            return False
            
    except Exception as e:
        print(f"[FAIL] V-API 连接失败：{e}")
        return False

async def test_llm_analysis():
    """测试 LLM 分析功能"""
    print("\n" + "="*70)
    print("测试 LLM 新闻分析功能")
    print("="*70)
    
    # 测试新闻样本
    test_title = "央行宣布降息 25 个基点以刺激经济增长"
    test_content = """
    中国人民银行今日宣布，下调贷款市场报价利率（LPR）25 个基点，
    这是今年以来的第二次降息。专家表示，此次降息将有助于降低
    企业融资成本，刺激投资和消费，促进经济复苏。
    
    市场分析人士认为，降息将对股市形成利好，尤其是对利率敏感
    的房地产和金融行业。同时，降息也可能对人民币汇率产生一定压力。
    """
    
    print(f"\n测试新闻标题：{test_title}")
    print(f"测试内容长度：{len(test_content)} 字")
    
    try:
        # 使用 V-API 进行快速分析
        print("\n使用 V-API 进行新闻分析...")
        print(f"使用模型：{settings.DEFAULT_LLM_MODEL}")
        
        result = await llm_engine.brief_analyze_with_vapi(
            title=test_title,
            content=test_content,
            model=settings.DEFAULT_LLM_MODEL
        )
        
        if result.get('error'):
            print(f"[FAIL] 分析失败：{result['error']}")
            return False
        
        print("\n[OK] 分析成功！")
        print(f"\n分析结果:")
        print(f"  摘要：{result.get('summary', 'N/A')[:100]}...")
        print(f"  关键词：{', '.join(result.get('keywords', [])[:5])}")
        print(f"  情感：{result.get('sentiment', 'N/A')}")
        print(f"  分类：{', '.join(result.get('categories', []))}")
        print(f"  重要性：{result.get('importance', 0)}/100")
        print(f"  多空判断：{result.get('position_bias', 'N/A')}")
        print(f"  多空幅度：{result.get('position_magnitude', 0)}%")
        print(f"  市场影响：{result.get('market_impact', 0)}/100")
        print(f"  行业相关性：{result.get('industry_relevance', 0)}/100")
        print(f"  新颖性：{result.get('novelty_score', 0)}/100")
        print(f"  紧急性：{result.get('urgency', 0)}/100")
        
        # Token 使用
        input_tokens = result.get('input_tokens', 0)
        output_tokens = result.get('output_tokens', 0)
        print(f"\n  Token 使用:")
        print(f"    输入：{input_tokens}")
        print(f"    输出：{output_tokens}")
        print(f"    总计：{input_tokens + output_tokens}")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM 分析失败：{e}")
        import traceback
        traceback.print_exc()
        return False

def check_configuration():
    """检查 AI 配置"""
    print("="*70)
    print("AI 配置检查")
    print("="*70)
    
    print(f"\n基础配置:")
    print(f"  VAPI_BASE_URL: {settings.VAPI_BASE_URL}")
    print(f"  VAPI_API_KEY: {'已配置' + ' (' + settings.VAPI_API_KEY[:15] + '...)' if settings.VAPI_API_KEY else '未配置'}")
    print(f"  DEFAULT_LLM_MODEL: {settings.DEFAULT_LLM_MODEL}")
    
    print(f"\n其他 AI 服务:")
    print(f"  OPENAI_API_KEY: {'已配置' if settings.OPENAI_API_KEY else '未配置'}")
    print(f"  DEEPSEEK_API_KEY: {'已配置' if settings.DEEPSEEK_API_KEY else '未配置'}")
    print(f"  ANTHROPIC_API_KEY: {'已配置' if settings.ANTHROPIC_API_KEY else '未配置'}")
    
    print(f"\n成本追踪:")
    print(f"  ENABLE_COST_TRACKING: {settings.ENABLE_COST_TRACKING}")
    print(f"  MONTHLY_BUDGET_USD: ${settings.MONTHLY_BUDGET_USD}")
    
    # 检查 LLM 引擎可用模型
    print(f"\nLLM 引擎可用模型:")
    available_models = llm_engine.get_available_models()
    for model in available_models:
        print(f"  - {model['id']} ({model['provider']})")

async def main():
    """主测试流程"""
    print("\n" + "="*70)
    print("LLMQuant News - AI 配置测试")
    print("="*70)
    
    # 1. 检查配置
    check_configuration()
    
    # 2. 测试 V-API 连接
    vapi_ok = await test_vapi_connection()
    
    # 3. 测试 LLM 分析
    if vapi_ok:
        llm_ok = await test_llm_analysis()
    else:
        print("\n⚠ 跳过 LLM 分析测试（V-API 未连接）")
        llm_ok = False
    
    # 4. 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    if vapi_ok and llm_ok:
        print("\n[SUCCESS] 所有测试通过！AI 配置正常。")
        print("\n建议:")
        print("  1. 可以开始使用 AI 新闻分析功能")
        print("  2. 监控 Token 使用情况")
        print("  3. 根据需求调整推送阈值")
    elif vapi_ok:
        print("\n[WARNING] V-API 连接正常，但分析测试失败")
        print("  请检查模型配置是否正确")
    else:
        print("\n[ERROR] AI 配置存在问题")
        print("  请检查:")
        print("  1. V-API API Key 是否正确")
        print("  2. 网络连接是否正常")
        print("  3. V-API 服务是否可用")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(main())
