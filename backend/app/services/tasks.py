# -*- coding: utf-8 -*-
"""
Celery 任务模块 - 爬虫和推送任务
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any

from app.services.celery_app import celery_app
from app.database import SessionLocal
from app.models import News, CrawlerConfig, UserConfig, PushLog
from app.services.news_service import CrawlerService, PushService
from app.crawler import crawler_manager
from app.scoring.engine import ScoringEngine
from app.llm import llm_engine
from app.config import settings


@celery_app.task(bind=True, max_retries=3)
def crawl_single_source(self, config_id: int):
    """爬取单个信息源"""
    db = SessionLocal()
    
    try:
        # 获取配置
        config = CrawlerService.get_config_by_id(db, config_id)
        if not config or not config.is_active:
            return {"status": "skipped", "reason": "Config not found or inactive"}
        
        # 创建爬虫实例
        crawler = crawler_manager.create_crawler(config.to_dict())
        if not crawler:
            return {"status": "error", "reason": "Failed to create crawler"}
        
        # 执行爬取（使用asyncio运行异步爬虫）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            news_items = loop.run_until_complete(crawler.crawl())
        finally:
            loop.close()
        
        # 处理爬取的新闻
        processed_count = 0
        for item in news_items:
            try:
                # 检查是否已存在（根据URL去重）
                existing = db.query(News).filter(News.url == item.url).first()
                if existing:
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
                
                # AI处理（直接调用）
                ai_scores = None
                try:
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
                    
                    # 更新新闻记录
                    if 'summary' in ai_result:
                        news.summary = ai_result['summary']
                    if 'categories' in ai_result:
                        news.categories = ai_result['categories']
                    if 'keywords' in ai_result:
                        news.keywords = ai_result['keywords']
                    if 'sentiment' in ai_result:
                        news.sentiment = ai_result['sentiment']
                    if 'scores' in ai_result:
                        scores = ai_result['scores']
                        news.ai_score = sum(scores.values()) / len(scores) if scores else 50
                        news.market_impact = scores.get('market_impact', 50)
                        news.industry_relevance = scores.get('industry_relevance', 50)
                        news.novelty_score = scores.get('novelty_score', 50)
                        news.urgency = scores.get('urgency', 50)
                    
                    # 更新分析状态
                    news.is_analyzed = True
                    news.analyzed_at = datetime.utcnow()
                    news.analysis_type = 'full'
                    
                    # 记录成本
                    if ai_result.get('cost'):
                        cost_data = ai_result['cost']
                        cost = llm_engine.calculate_cost(
                            ai_result.get('model_used', 'deepseek-chat'),
                            cost_data.get('input_tokens', 0),
                            cost_data.get('output_tokens', 0)
                        )
                        from app.services.news_service import CostService
                        CostService.record_cost(
                            db,
                            model=ai_result.get('model_used', 'deepseek-chat'),
                            provider='openai',
                            prompt_tokens=cost_data.get('input_tokens', 0),
                            completion_tokens=cost_data.get('output_tokens', 0),
                            cost_usd=cost['cost_usd'],
                            cost_cny=cost['cost_cny'],
                            request_type='news_analysis',
                            news_id=news.id
                        )
                    
                    print(f"AI处理成功: {news.title}")
                    
                except Exception as e:
                    print(f"AI处理失败: {e}")
                
                # 评分计算
                from app.scoring.engine import NewsScorer
                scorer = NewsScorer({})
                
                # 准备AI评分数据
                ai_scores_data = {}
                if ai_scores:
                    ai_scores_data = {
                        'market_impact': ai_scores.get('market_impact', 50),
                        'industry_relevance': ai_scores.get('industry_relevance', 50),
                        'novelty_score': ai_scores.get('novelty_score', 50),
                        'urgency': ai_scores.get('urgency', 50),
                    }
                    news.ai_score = ai_scores.get('ai_score', 50)
                
                # 计算综合评分
                news_data = news.to_dict()
                score_result = scorer.calculate_final_score(ai_scores_data, news_data)
                
                news.rule_score = score_result['rule_score']
                news.final_score = score_result['final_score']
                
                processed_count += 1
                
            except Exception as e:
                print(f"处理新闻失败: {e}")
                continue
        
        # 提交所有更改
        db.commit()
        
        # 更新爬虫统计
        CrawlerService.update_stats(db, config_id, success=True)
        
        # 自动推送高分新闻
        if config.priority >= 8:  # 高优先级源自动推送
            push_high_score_news(db)
        
        return {
            "status": "success",
            "crawled": len(news_items),
            "processed": processed_count,
            "source": config.name
        }
        
    except Exception as exc:
        # 更新爬虫错误统计
        try:
            CrawlerService.update_stats(db, config_id, success=False, error_msg=str(exc))
            db.commit()
        except:
            pass
        
        # 重试逻辑
        if self.request.retries < 3:
            raise self.retry(exc=exc, countdown=60)
        
        return {"status": "error", "reason": str(exc)}
        
    finally:
        db.close()


@celery_app.task
def crawl_all_sources():
    """爬取所有活跃信息源"""
    db = SessionLocal()
    
    try:
        # 获取所有活跃的配置
        configs = CrawlerService.get_active_configs(db)
        
        results = []
        for config in configs:
            # 触发单个源爬取任务
            result = crawl_single_source.delay(config.id)
            results.append({
                "source": config.name,
                "task_id": result.id
            })
        
        return {
            "status": "success",
            "total_sources": len(configs),
            "tasks": results
        }
        
    finally:
        db.close()


@celery_app.task
def push_high_score_news(db_session=None, min_score: float = None):
    """推送高分新闻到配置的渠道"""
    if db_session:
        db = db_session
        should_close = False
    else:
        db = SessionLocal()
        should_close = True
    
    try:
        # 获取阈值
        if min_score is None:
            min_score = settings.SCORE_THRESHOLD
        
        # 获取用户配置
        user_config = db.query(UserConfig).filter(UserConfig.user_id == "default").first()
        if not user_config or not user_config.push_enabled:
            return {"status": "skipped", "reason": "Push disabled"}
        
        # 获取未推送的高分新闻
        news_to_push = db.query(News).filter(
            News.is_pushed == False,
            News.final_score >= min_score
        ).order_by(News.final_score.desc()).limit(10).all()
        
        if not news_to_push:
            return {"status": "no_news", "count": 0}
        
        # 获取推送渠道
        channels = user_config.push_channels or []
        if not channels:
            return {"status": "skipped", "reason": "No push channels configured"}
        
        # 执行推送
        pushed_count = 0
        for news in news_to_push:
            try:
                # 使用asyncio运行异步推送
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    result = loop.run_until_complete(
                        PushService.push_news(db, news, channels, user_config)
                    )
                    
                    if result.get('success'):
                        pushed_count += 1
                        
                finally:
                    loop.close()
                    
            except Exception as e:
                print(f"推送失败 [{news.id}]: {e}")
                continue
        
        db.commit()
        
        return {
            "status": "success",
            "pushed": pushed_count,
            "total": len(news_to_push)
        }
        
    finally:
        if should_close:
            db.close()


@celery_app.task
def process_news_with_ai(db_session=None, news_item=None):
    """使用AI处理新闻（分类、评分、摘要）"""
    if not news_item:
        return {"status": "skipped", "reason": "No news item"}
    
    try:
        # 使用LLM引擎处理
        if hasattr(llm_engine, 'process_news'):
            # 使用asyncio运行异步方法
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    llm_engine.process_news(
                        news_item.title,
                        news_item.content or ''
                    )
                )
            finally:
                loop.close()
            
            # 更新新闻记录
            if 'summary' in result:
                news_item.summary = result['summary']
            if 'categories' in result:
                news_item.categories = result['categories']
            if 'keywords' in result:
                news_item.keywords = result['keywords']
            if 'sentiment' in result:
                news_item.sentiment = result['sentiment']
            if 'scores' in result:
                scores = result['scores']
                news_item.ai_score = sum(scores.values()) / len(scores) if scores else 50
                news_item.market_impact = scores.get('market_impact', 50)
                news_item.industry_relevance = scores.get('industry_relevance', 50)
                news_item.novelty_score = scores.get('novelty_score', 50)
                news_item.urgency = scores.get('urgency', 50)
            
            # 更新分析状态
            news_item.is_analyzed = True
            news_item.analyzed_at = datetime.utcnow()
            news_item.analysis_type = 'full'
            
            return {"status": "success", "result": result}
        
        return {"status": "skipped", "reason": "LLM engine not available"}
        
    except Exception as e:
        return {"status": "error", "reason": str(e)}


@celery_app.task
def cleanup_old_news(days: int = 30):
    """清理旧新闻"""
    db = SessionLocal()
    
    try:
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 删除旧新闻
        deleted = db.query(News).filter(News.crawled_at < cutoff_date).delete()
        db.commit()
        
        return {
            "status": "success",
            "deleted": deleted
        }
        
    except Exception as e:
        return {"status": "error", "reason": str(e)}
        
    finally:
        db.close()
