#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫和AI分析功能
"""

import asyncio
from app.database import SessionLocal
from app.services.news_service import CrawlerService
from app.crawler import crawler_manager
from app.llm import llm_engine
from app.models import News


def test_crawler_ai():
    """测试爬虫和AI分析"""
    db = SessionLocal()
    
    try:
        # 获取活跃的爬虫配置
        configs = CrawlerService.get_active_configs(db)
        print(f"找到 {len(configs)} 个活跃的爬虫配置")
        
        if not configs:
            print("没有活跃的爬虫配置")
            return
        
        # 测试第二个配置
        config = configs[1]
        print(f"测试爬虫: {config.name}")
        
        # 创建爬虫实例
        crawler = crawler_manager.create_crawler(config.to_dict())
        if not crawler:
            print("创建爬虫失败")
            return
        
        # 执行爬取
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            news_items = loop.run_until_complete(crawler.crawl())
            print(f"爬取到 {len(news_items)} 条新闻")
            
            if not news_items:
                print("没有爬取到新闻")
                return
            
            # 处理第一条新闻
            item = news_items[0]
            print(f"\n处理新闻: {item.title}")
            
            # 检查是否已存在
            existing = db.query(News).filter(News.url == item.url).first()
            if existing:
                print("新闻已存在，跳过")
                return
            
            # 创建新闻记录
            from datetime import datetime
            
            news = News(
                title=item.title,
                content=item.content or "",
                summary=item.summary or "",
                url=item.url,
                source=config.name,
                source_type=config.crawler_type,
                author=item.author,
                published_at=item.published_at,
                categories=item.categories or [],
                crawled_at=datetime.utcnow()
            )
            db.add(news)
            db.flush()  # 获取ID
            
            print(f"创建新闻记录成功，ID: {news.id}")
            
            # 测试AI分析
            print("\n开始AI分析...")
            
            try:
                # 启用LiteLLM的详细日志
                import litellm
                litellm.set_verbose(True)
                
                # 使用asyncio运行异步AI处理
                ai_result = loop.run_until_complete(
                    llm_engine.process_news(
                        news.title,
                        news.content or ''
                    )
                )
                
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
                
        finally:
            loop.close()
            
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_crawler_ai()
