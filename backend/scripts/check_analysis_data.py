#!/usr/bin/env python3
"""
检查数据库中是否存在已分析的新闻数据
"""
import sqlite3
import sys

# 数据库路径
DB_PATH = '../data/llmquant.db'

def check_analysis_data():
    """检查数据库中的分析数据"""
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=== 数据库分析数据检查 ===")
        
        # 1. 检查news表结构
        print("\n1. 检查news表结构:")
        cursor.execute("PRAGMA table_info(news)")
        columns = cursor.fetchall()
        analysis_columns = []
        for col in columns:
            col_name = col[1]
            if any(keyword in col_name for keyword in ['ai_', 'sentiment', 'market_', 'industry_', 'novelty_', 'urgency', 'is_analyzed']):
                analysis_columns.append(col_name)
                print(f"  - {col_name} (分析相关字段)")
            else:
                print(f"  - {col_name}")
        
        # 2. 检查新闻总数
        print("\n2. 检查新闻数量:")
        cursor.execute("SELECT COUNT(*) FROM news")
        total_news = cursor.fetchone()[0]
        print(f"  新闻总数: {total_news}")
        
        # 3. 检查已分析的新闻
        print("\n3. 检查已分析的新闻:")
        cursor.execute("SELECT COUNT(*) FROM news WHERE is_analyzed = 1")
        analyzed_count = cursor.fetchone()[0]
        print(f"  已分析新闻数: {analyzed_count}")
        print(f"  分析率: {analyzed_count/total_news*100:.2f}%" if total_news > 0 else "  分析率: 0% (无新闻数据)")
        
        # 4. 检查分析数据详情
        print("\n4. 分析数据详情:")
        cursor.execute("""
            SELECT 
                id, title, ai_score, sentiment, market_impact, 
                industry_relevance, novelty_score, urgency, is_analyzed
            FROM news 
            WHERE is_analyzed = 1 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        analyzed_news = cursor.fetchall()
        
        if analyzed_news:
            print("  最近5条已分析新闻:")
            for news in analyzed_news:
                id_, title, ai_score, sentiment, market_impact, industry_relevance, novelty_score, urgency, is_analyzed = news
                print(f"  ID: {id_}")
                print(f"  标题: {title[:50]}..." if len(title) > 50 else f"  标题: {title}")
                print(f"  AI评分: {ai_score}")
                print(f"  情感分析: {sentiment}")
                print(f"  市场影响: {market_impact}")
                print(f"  行业相关: {industry_relevance}")
                print(f"  新颖度: {novelty_score}")
                print(f"  紧急度: {urgency}")
                print(f"  分析状态: {'已分析' if is_analyzed else '未分析'}")
                print("  " + "-" * 60)
        else:
            print("  暂无已分析的新闻数据")
        
        # 5. 检查未分析的新闻
        print("\n5. 检查未分析的新闻:")
        cursor.execute("SELECT COUNT(*) FROM news WHERE is_analyzed = 0")
        unanalyzed_count = cursor.fetchone()[0]
        print(f"  未分析新闻数: {unanalyzed_count}")
        
        if unanalyzed_count > 0:
            cursor.execute("""
                SELECT id, title, created_at 
                FROM news 
                WHERE is_analyzed = 0 
                ORDER BY created_at DESC 
                LIMIT 3
            """)
            unanalyzed_news = cursor.fetchall()
            print("  最近3条未分析新闻:")
            for news in unanalyzed_news:
                id_, title, created_at = news
                print(f"  ID: {id_}")
                print(f"  标题: {title[:50]}..." if len(title) > 50 else f"  标题: {title}")
                print(f"  创建时间: {created_at}")
                print("  " + "-" * 60)
        
        # 关闭连接
        conn.close()
        
        return analyzed_count > 0
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")
        return False

if __name__ == "__main__":
    has_analysis_data = check_analysis_data()
    print(f"\n=== 检查结果 ===")
    print(f"数据库中{'存在' if has_analysis_data else '不存在'}已分析的新闻数据")
    sys.exit(0 if has_analysis_data else 1)
