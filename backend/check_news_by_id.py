#!/usr/bin/env python3
"""
检查特定新闻ID的AI分析字段
"""
import sqlite3

DB_PATH = '../data/llmquant.db'

def check_news_by_id(news_id: int):
    """检查指定新闻ID的AI分析字段"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, title, 
            ai_score, market_impact, industry_relevance, 
            novelty_score, urgency, sentiment, is_analyzed
        FROM news 
        WHERE id = ?
    """, (news_id,))
    
    result = cursor.fetchone()
    
    if result:
        id_, title, ai_score, market_impact, industry_relevance, novelty_score, urgency, sentiment, is_analyzed = result
        print(f"新闻 ID: {id_}")
        print(f"标题: {title}")
        print(f"ai_score: {ai_score}")
        print(f"market_impact: {market_impact}")
        print(f"industry_relevance: {industry_relevance}")
        print(f"novelty_score: {novelty_score}")
        print(f"urgency: {urgency}")
        print(f"sentiment: {sentiment}")
        print(f"is_analyzed: {is_analyzed}")
    else:
        print(f"未找到新闻 ID: {news_id}")
    
    conn.close()

if __name__ == "__main__":
    import sys
    news_id = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    check_news_by_id(news_id)
