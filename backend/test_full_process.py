#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的爬虫、AI分析和消息去重流程
"""

import asyncio
from app.database import SessionLocal
from app.models import News
from app.services.news_service import CrawlerService
from app.crawler import crawler_manager
from app.llm import llm_engine
from datetime import datetime, timedelta


def test_full_process():
    """测试完整的流程"""
    db = SessionLocal()
    
    try:
        print("开始测试完整流程...")
        
        # 获取活跃的爬虫配置
        configs = CrawlerService.get_active_configs(db)
        print(f"找到 {len(configs)} 个活跃的爬虫配置")
        
        if not configs:
            print("没有活跃的爬虫配置，测试结束")
            return
        
        # 选择一个配置进行测试
        config = configs[0]
        print(f"测试爬虫: {config.name}")
        
        # 创建爬虫实例
        crawler = crawler_manager.create_crawler(config.to_dict())
        if not crawler:
            print("创建爬虫失败，测试结束")
            return
        
        # 执行爬取
        print("开始爬取新闻...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            news_items = loop.run_until_complete(crawler.crawl())
        finally:
            loop.close()
            
        print(f"爬取到 {len(news_items)} 条新闻")
        
        if not news_items:
            print("没有爬取到新闻，测试结束")
            return
        
        # 处理新闻
        processed_count = 0
        duplicate_count = 0
        
        for item in news_items:
            print(f"\n处理新闻: {item.title}")
            
            # 检查是否已存在（根据URL去重）
            existing = db.query(News).filter(News.url == item.url).first()
            if existing:
                print(f"✅ 新闻已存在（URL重复）: {item.title}")
                duplicate_count += 1
                continue
            
            # 检查内容相似性（基于标题和内容）
            from sqlalchemy import or_
            existing_by_content = db.query(News).filter(
                or_(
                    News.title == item.title,
                    News.content == item.content
                ),
                News.crawled_at >= datetime.utcnow() - timedelta(days=1)
            ).first()
            
            if existing_by_content:
                print(f"✅ 新闻已存在（内容重复）: {item.title}")
                duplicate_count += 1
                continue
            
            # 创建新闻记录
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
            print("开始AI分析...")
            
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
                
                # 检查是否有错误
                if 'error' in ai_result:
                    print(f"⚠️  AI分析错误: {ai_result['error']}")
                    # 即使有错误，也尝试更新可用的结果
                
                # 更新新闻记录
                if 'summary' in ai_result:
                    news.summary = ai_result['summary']
                    print(f"生成摘要: {ai_result['summary'][:100]}...")
                if 'categories' in ai_result:
                    news.categories = ai_result['categories']
                    print(f"分类: {ai_result['categories']}")
                if 'keywords' in ai_result:
                    news.keywords = ai_result['keywords']
                    print(f"关键词: {ai_result['keywords']}")
                if 'sentiment' in ai_result:
                    news.sentiment = ai_result['sentiment']
                    print(f"情感: {ai_result['sentiment']}")
                if 'scores' in ai_result:
                    scores = ai_result['scores']
                    news.ai_score = sum(scores.values()) / len(scores) if scores else 50
                    print(f"评分: {scores}")
                
                # 更新分析状态
                news.is_analyzed = True
                news.analyzed_at = datetime.utcnow()
                news.analysis_type = 'full'
                
                print("AI分析成功")
                
            except Exception as e:
                import traceback
                error_msg = f"AI处理失败: {e}\n{traceback.format_exc()}"
                print(error_msg)
                # 即使AI分析失败，也继续处理新闻
                # 设置默认值，确保新闻记录完整
                news.is_analyzed = False
                news.ai_score = 50  # 默认评分
                news.summary = f"AI分析失败: {str(e)}"
                news.sentiment = 'neutral'  # 默认情感
                news.keywords = []  # 默认关键词
                news.categories = []  # 默认分类
            
            processed_count += 1
            
            # 限制处理数量，避免测试时间过长
            if processed_count >= 2:
                print("\n测试数量限制，停止处理")
                break
        
        # 提交更改
        db.commit()
        
        print(f"\n测试完成:")
        print(f"- 处理新闻数: {processed_count}")
        print(f"- 重复新闻数: {duplicate_count}")
        print(f"- 总新闻数: {len(news_items)}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_full_process()
