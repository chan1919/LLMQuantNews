#!/usr/bin/env python3
"""
测试分析流程：创建测试新闻并验证分析状态
"""

import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import get_db
from app.models import News
from app.schemas import NewsCreate
from app.services.news_service import NewsService

async def test_analysis_flow():
    """
    测试分析流程
    """
    print("开始测试分析流程...")
    print("=" * 50)
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 1. 获取当前未分析新闻数量
        unanalyzed_count = NewsService.get_unanalyzed_news_count(db)
        print(f"当前未分析新闻数量: {unanalyzed_count}")
        
        # 2. 创建测试新闻
        test_news_data = NewsCreate(
            title="测试新闻：人工智能在量化交易中的应用",
            content="人工智能技术正在改变量化交易的格局。通过机器学习算法，交易员可以更准确地预测市场走势，提高交易效率。\n\n近年来，深度学习模型在金融市场中的应用越来越广泛，从基本面分析到技术指标，AI都展现出了强大的能力。\n\n专家预测，未来5年内，AI驱动的量化交易将占据市场的30%以上份额。",
            url="http://example.com/test-news-1",
            source="测试来源",
            source_type="web",
            published_at=datetime.utcnow()
        )
        
        # 创建新闻记录
        test_news = News(**test_news_data.model_dump())
        db.add(test_news)
        db.commit()
        db.refresh(test_news)
        
        print(f"\n创建测试新闻成功，ID: {test_news.id}")
        print(f"新闻标题: {test_news.title}")
        print(f"初始分析状态: 已分析={test_news.is_analyzed}")
        
        # 3. 再次获取未分析新闻数量
        new_unanalyzed_count = NewsService.get_unanalyzed_news_count(db)
        print(f"\n创建测试新闻后未分析数量: {new_unanalyzed_count}")
        
        # 4. 执行分析
        print("\n开始使用V-API分析未分析新闻...")
        analysis_result = await NewsService.analyze_unanalyzed_news(db, limit=10)
        print(f"分析结果: {analysis_result}")
        
        # 5. 验证分析结果
        db.refresh(test_news)
        print(f"\n测试新闻分析状态:")
        print(f"已分析: {test_news.is_analyzed}")
        print(f"分析类型: {test_news.analysis_type}")
        print(f"分析时间: {test_news.analyzed_at}")
        print(f"摘要: {test_news.summary}")
        print(f"关键词: {test_news.keywords}")
        print(f"分类: {test_news.categories}")
        print(f"情感: {test_news.sentiment}")
        print(f"AI评分: {test_news.ai_score}")
        print(f"最终评分: {test_news.final_score}")
        
        # 6. 最后检查未分析数量
        final_unanalyzed_count = NewsService.get_unanalyzed_news_count(db)
        print(f"\n分析完成后未分析数量: {final_unanalyzed_count}")
        
        print("\n" + "=" * 50)
        print("测试分析流程完成！")
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试数据
        if 'test_news' in locals():
            db.delete(test_news)
            db.commit()
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_analysis_flow())
