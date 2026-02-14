#!/usr/bin/env python3
"""
直接用SQL更新AI分析字段
"""
import sqlite3

DB_PATH = '../data/llmquant.db'

def update_ai_fields():
    """更新AI分析字段"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 更新新闻ID 1的AI分析字段
    cursor.execute("""
        UPDATE news 
        SET ai_score = 72.5,
            market_impact = 85,
            industry_relevance = 70,
            novelty_score = 60,
            urgency = 75,
            sentiment = 'neutral',
            is_analyzed = 1
        WHERE id = 1
    """)
    
    conn.commit()
    print(f"更新了 {cursor.rowcount} 条记录")
    
    # 验证更新
    cursor.execute("SELECT id, ai_score, market_impact, sentiment FROM news WHERE id = 1")
    result = cursor.fetchone()
    print(f"验证结果: {result}")
    
    conn.close()

if __name__ == "__main__":
    update_ai_fields()
