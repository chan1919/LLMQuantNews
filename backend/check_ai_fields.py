#!/usr/bin/env python3
"""
检查数据库中新闻的AI分析字段实际值
"""
import sqlite3

DB_PATH = '../data/llmquant.db'

def check_ai_fields():
    """检查AI分析字段的实际值"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=== 检查AI分析字段实际值 ===\n")
    
    # 检查前5条新闻的AI分析字段
    cursor.execute("""
        SELECT 
            id, title, 
            ai_score, market_impact, industry_relevance, 
            novelty_score, urgency, sentiment, is_analyzed
        FROM news 
        ORDER BY id DESC 
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    
    for row in results:
        id_, title, ai_score, market_impact, industry_relevance, novelty_score, urgency, sentiment, is_analyzed = row
        print(f"ID: {id_}")
        print(f"标题: {title[:50]}..." if len(title) > 50 else f"标题: {title}")
        print(f"  ai_score: {ai_score}")
        print(f"  market_impact: {market_impact}")
        print(f"  industry_relevance: {industry_relevance}")
        print(f"  novelty_score: {novelty_score}")
        print(f"  urgency: {urgency}")
        print(f"  sentiment: {sentiment}")
        print(f"  is_analyzed: {is_analyzed}")
        print("-" * 60)
    
    # 统计有AI分析数据的新闻数量
    cursor.execute("SELECT COUNT(*) FROM news WHERE ai_score IS NOT NULL AND ai_score > 0")
    has_ai_score = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM news WHERE is_analyzed = 1")
    is_analyzed_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM news")
    total = cursor.fetchone()[0]
    
    print(f"\n统计信息:")
    print(f"  总新闻数: {total}")
    print(f"  有AI评分的新闻数: {has_ai_score}")
    print(f"  标记为已分析的新闻数: {is_analyzed_count}")
    
    conn.close()

if __name__ == "__main__":
    check_ai_fields()
