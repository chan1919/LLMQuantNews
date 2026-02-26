#!/usr/bin/env python3
"""
AI 新闻分析脚本 - 使用 V-API
"""
import sys
import asyncio
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import News
from app.scoring.engine import NewsScorer
from datetime import datetime
import litellm

async def analyze_news_batch():
    """批量分析新闻"""
    from app.config import settings
    
    db = SessionLocal()
    
    # V-API 配置
    api_base = f"{settings.VAPI_BASE_URL}/v1"
    api_key = settings.VAPI_API_KEY
    
    # 获取未分析的新闻
    news_list = db.query(News).filter(News.is_analyzed == False).limit(5).all()
    
    print(f'待分析新闻：{len(news_list)} 条\n')
    
    success_count = 0
    
    for news in news_list:
        print(f'分析 ID {news.id}: {news.title[:50]}...')
        
        try:
            # 构建 prompt
            content = news.content[:1000] if news.content else news.title
            prompt = f"""Analyze this news and return ONLY valid JSON (no markdown, no extra text):

Title: {news.title}
Content: {content}

{{{{
    "summary": "brief summary under 50 words",
    "keywords": ["kw1", "kw2", "kw3"],
    "sentiment": "positive or negative or neutral",
    "categories": ["Finance"],
    "importance": 75,
    "position_bias": "bullish or bearish or neutral",
    "position_magnitude": 60,
    "market_impact": 70,
    "industry_relevance": 65,
    "novelty_score": 50,
    "urgency": 60
}}}}

Return ONLY the JSON, nothing else:"""
            
            # 调用 V-API
            response = await litellm.acompletion(
                model="openai/deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                api_base=api_base,
                api_key=api_key,
                temperature=0.3,
                max_tokens=400,
            )
            
            # 解析结果
            import json
            result = json.loads(response.choices[0].message.content)
            
            # 更新新闻
            news.summary = result.get('summary', '')[:500]
            news.keywords = result.get('keywords', [])[:10]
            news.categories = result.get('categories', [])[:5]
            news.sentiment = result.get('sentiment', 'neutral')
            news.ai_score = result.get('importance', 50)
            news.market_impact = result.get('market_impact', 50)
            news.industry_relevance = result.get('industry_relevance', 50)
            news.novelty_score = result.get('novelty_score', 50)
            news.urgency = result.get('urgency', 50)
            news.position_bias = result.get('position_bias', 'neutral')
            news.position_magnitude = result.get('position_magnitude', 0)
            
            # 计算最终分数
            scorer = NewsScorer({})
            ai_scores = {
                'market_impact': news.market_impact,
                'industry_relevance': news.industry_relevance,
                'novelty_score': news.novelty_score,
                'urgency': news.urgency,
            }
            score_result = scorer.calculate_final_score(ai_scores, {
                'title': news.title,
                'content': news.content or '',
                'categories': news.categories
            })
            news.final_score = score_result['final_score']
            news.rule_score = score_result['rule_score']
            
            # 状态更新
            news.is_analyzed = True
            news.analyzed_at = datetime.utcnow()
            news.analysis_type = 'vapi'
            news.llm_model_used = 'deepseek-chat'
            
            db.commit()
            print(f'  OK - score: {news.final_score}')
            success_count += 1
            
        except Exception as e:
            print(f'  FAIL: {e}')
            db.rollback()
    
    db.close()
    
    print(f'\n完成：{success_count}/{len(news_list)}')
    return success_count

if __name__ == "__main__":
    result = asyncio.run(analyze_news_batch())
    sys.exit(0 if result > 0 else 1)
