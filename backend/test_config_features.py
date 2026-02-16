#!/usr/bin/env python3
"""
测试配置分析API
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.config_analysis import config_analysis_service
from app.database import SessionLocal
from app.services.news_service import ConfigService

async def test_config_analysis():
    """测试配置分析功能"""
    
    # 测试描述
    test_description = """
    我是A股价值投资者，主要关注科技和新能源板块，对政策变化非常敏感。
    我不喜欢短期炒作的消息，更关注公司的基本面和长期发展趋势。
    希望看到权威媒体的深度分析，特别是关于产业政策和技术突破的报道。
    """
    
    print("="*70)
    print("测试AI配置分析")
    print("="*70)
    print(f"\n用户描述:\n{test_description}\n")
    
    try:
        # 调用AI分析
        result = await config_analysis_service.analyze_description(test_description)
        
        print("\n" + "="*70)
        print("AI分析结果")
        print("="*70)
        
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n" + "="*70)
        print("测试完成!")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_news_filter():
    """测试新闻筛选功能"""
    print("\n" + "="*70)
    print("测试新闻筛选")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        from app.services.news_filter import news_filter_service
        from app.services.news_service import ConfigService
        
        # 获取用户配置
        user_config = ConfigService.get_user_config(db)
        
        # 测试筛选
        news_list = news_filter_service.filter_news_by_config(
            db=db,
            user_config=user_config,
            mode="important",
            limit=5
        )
        
        print(f"\n筛选到 {len(news_list)} 条新闻")
        
        for i, news in enumerate(news_list, 1):
            relevance = getattr(news, 'user_relevance_score', 0)
            print(f"\n{i}. [{news.source}] {news.title[:50]}...")
            print(f"   分数: {news.final_score:.1f} | 相关度: {relevance:.1f}")
        
        print("\n" + "="*70)
        print("测试完成!")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # 运行配置分析测试
    success1 = asyncio.run(test_config_analysis())
    
    # 运行新闻筛选测试
    success2 = test_news_filter()
    
    if success1 and success2:
        print("\n所有测试通过!")
    else:
        print("\n部分测试失败")
