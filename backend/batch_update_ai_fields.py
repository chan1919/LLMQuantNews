#!/usr/bin/env python3
"""
批量更新AI分析字段
"""
import sqlite3

DB_PATH = '../data/llmquant.db'

def batch_update_ai_fields():
    """批量更新AI分析字段"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有AI评分为0的新闻
    cursor.execute("SELECT id, title FROM news WHERE ai_score = 0 OR ai_score IS NULL LIMIT 10")
    news_list = cursor.fetchall()
    
    print(f"找到 {len(news_list)} 条需要更新的新闻")
    
    # 为每条新闻设置模拟的AI分析数据
    for news_id, title in news_list:
        # 根据标题内容设置不同的评分
        if '美联储' in title or '降息' in title or '利率' in title:
            ai_score = 72.5
            market_impact = 85
            industry_relevance = 70
            novelty_score = 60
            urgency = 75
            sentiment = 'neutral'
        elif 'AI' in title or '人工智能' in title:
            ai_score = 68.0
            market_impact = 70
            industry_relevance = 85
            novelty_score = 75
            urgency = 60
            sentiment = 'positive'
        else:
            ai_score = 50.0
            market_impact = 50
            industry_relevance = 50
            novelty_score = 50
            urgency = 50
            sentiment = 'neutral'
        
        cursor.execute("""
            UPDATE news 
            SET ai_score = ?,
                market_impact = ?,
                industry_relevance = ?,
                novelty_score = ?,
                urgency = ?,
                sentiment = ?,
                is_analyzed = 1
            WHERE id = ?
        """, (ai_score, market_impact, industry_relevance, novelty_score, urgency, sentiment, news_id))
        
        print(f"更新新闻 ID {news_id}: {title[:30]}... -> AI评分: {ai_score}")
    
    conn.commit()
    print(f"\n共更新了 {cursor.rowcount} 条记录")
    
    # 验证更新
    cursor.execute("SELECT id, ai_score, market_impact, sentiment FROM news WHERE ai_score > 0 LIMIT 5")
    results = cursor.fetchall()
    print("\n验证结果:")
    for row in results:
        print(f"  ID: {row[0]}, AI评分: {row[1]}, 市场影响: {row[2]}, 情感: {row[3]}")
    
    conn.close()

if __name__ == "__main__":
    batch_update_ai_fields()
