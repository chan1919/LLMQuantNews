#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新分析数据库中AI评分为0的新闻
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import News
from app.llm import llm_engine
from datetime import datetime


def reanalyze_news(limit: int = 10):
    """重新分析AI评分为0的新闻"""
    db = SessionLocal()
    
    try:
        # 查询AI评分为0的新闻
        news_list = db.query(News).filter(
            (News.ai_score == 0) | (News.ai_score == None)
        ).order_by(News.crawled_at.desc()).limit(limit).all()
        
        print(f"找到 {len(news_list)} 条需要重新分析的新闻")
        
        for idx, news in enumerate(news_list, 1):
            print(f"\n{'='*60}")
            print(f"[{idx}/{len(news_list)}] 处理新闻 ID: {news.id}")
            print(f"标题: {news.title[:50]}..." if len(news.title) > 50 else f"标题: {news.title}")
            
            try:
                # 执行AI分析
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
                
                # 检查是否有错误
                if 'error' in ai_result:
                    print(f"AI分析错误: {ai_result['error']}")
                    continue
                
                # 更新新闻记录
                if 'summary' in ai_result and ai_result['summary']:
                    news.summary = ai_result['summary']
                    print(f"摘要: {ai_result['summary'][:80]}...")
                
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
                    news.market_impact = scores.get('market_impact', 50)
                    news.industry_relevance = scores.get('industry_relevance', 50)
                    news.novelty_score = scores.get('novelty_score', 50)
                    news.urgency = scores.get('urgency', 50)
                    print(f"AI评分: {news.ai_score:.1f}")
                    print(f"市场影响: {news.market_impact}, 行业相关: {news.industry_relevance}")
                    print(f"新颖度: {news.novelty_score}, 紧急度: {news.urgency}")
                
                # 更新分析状态
                news.is_analyzed = True
                news.analyzed_at = datetime.utcnow()
                news.analysis_type = 'full'
                
                # 提交更改
                db.commit()
                print("✅ 分析成功并保存")
                
            except Exception as e:
                print(f"❌ 处理失败: {e}")
                db.rollback()
                continue
        
        print(f"\n{'='*60}")
        print(f"重新分析完成，共处理 {len(news_list)} 条新闻")
        
    finally:
        db.close()


if __name__ == "__main__":
    # 默认分析10条，可以通过参数指定数量
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    print(f"开始重新分析AI评分为0的新闻，限制数量: {limit}")
    reanalyze_news(limit)
