#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI分析功能
"""

import asyncio
from app.database import SessionLocal
from app.llm import llm_engine
from app.models import News


def test_ai_analysis():
    """测试AI分析"""
    db = SessionLocal()
    
    try:
        # 创建测试新闻记录
        from datetime import datetime
        
        # 生成唯一的URL
        import uuid
        unique_url = f"https://example.com/test-{uuid.uuid4()}"
        
        news = News(
            title="美联储宣布降息25个基点，市场反应积极",
            content="美联储在周三的货币政策会议上宣布降息25个基点，将联邦基金利率目标区间下调至1.5%-1.75%。这是美联储自2019年以来的首次降息。美联储主席鲍威尔在新闻发布会上表示，此次降息是为了应对全球经济增长放缓和贸易不确定性带来的风险，同时通胀仍低于2%的目标水平。市场对此反应积极，道琼斯工业平均指数上涨超过300点，标普500指数和纳斯达克综合指数也均有不同程度的上涨。分析师认为，此次降息可能为美国经济提供一定的刺激，但也反映了美联储对经济前景的担忧。",
            summary="",
            url=unique_url,
            source="测试新闻",
            source_type="test",
            author="测试作者",
            published_at=datetime.utcnow(),
            categories=[],
            crawled_at=datetime.utcnow()
        )
        db.add(news)
        db.flush()  # 获取ID
        
        print(f"创建测试新闻记录成功，ID: {news.id}")
        print(f"新闻标题: {news.title}")
        print(f"新闻内容: {news.content[:100]}...")
            
        # 测试AI分析
        print("\n开始AI分析...")
        
        try:
            # 启用LiteLLM的详细日志
            import litellm
            litellm.verbose = True
            
            # 使用asyncio运行异步AI处理
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                ai_result = loop.run_until_complete(
                    llm_engine.process_news(
                        news.title,
                        news.content or ''
                    )
                )
            finally:
                loop.close()
                
            print(f"AI分析结果: {ai_result}")
            print(f"AI分析成功: {ai_result.get('tasks_completed', [])}")
            
            # 检查是否有错误
            if 'error' in ai_result:
                print(f"AI分析错误: {ai_result['error']}")
            
            # 更新新闻记录
            if 'summary' in ai_result:
                news.summary = ai_result['summary']
                print(f"\n生成摘要: {ai_result['summary']}")
            
            if 'categories' in ai_result:
                news.categories = ai_result['categories']
                print(f"\n分类: {ai_result['categories']}")
            
            if 'keywords' in ai_result:
                news.keywords = ai_result['keywords']
                print(f"\n关键词: {ai_result['keywords']}")
            
            if 'sentiment' in ai_result:
                news.sentiment = ai_result['sentiment']
                print(f"\n情感: {ai_result['sentiment']}")
            
            if 'scores' in ai_result:
                scores = ai_result['scores']
                news.ai_score = sum(scores.values()) / len(scores) if scores else 50
                news.market_impact = scores.get('market_impact', 50)
                news.industry_relevance = scores.get('industry_relevance', 50)
                news.novelty_score = scores.get('novelty_score', 50)
                news.urgency = scores.get('urgency', 50)
                print(f"\n评分: {scores}")
            
            # 更新分析状态
            news.is_analyzed = True
            news.analyzed_at = datetime.utcnow()
            news.analysis_type = 'full'
            
            # 提交更改
            db.commit()
            print("\nAI分析完成并更新数据库")
            
        except Exception as e:
            print(f"\nAI分析失败: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_ai_analysis()
