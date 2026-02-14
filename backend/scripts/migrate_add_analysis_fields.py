#!/usr/bin/env python3
"""
数据库迁移脚本：为News表添加分析状态字段
"""

import sqlite3
import os
from datetime import datetime

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'llmquant.db')

def migrate_database():
    """
    执行数据库迁移，添加分析状态相关字段
    """
    conn = None
    try:
        # 连接到数据库
        print(f"尝试连接到数据库: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查is_analyzed字段是否存在
        cursor.execute("PRAGMA table_info(news)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"当前表结构: {columns}")
        
        # 添加is_analyzed字段
        if 'is_analyzed' not in columns:
            cursor.execute("ALTER TABLE news ADD COLUMN is_analyzed INTEGER DEFAULT 0")
            print("✓ 添加is_analyzed字段成功")
        else:
            print("⚠ is_analyzed字段已存在")
        
        # 添加analyzed_at字段
        if 'analyzed_at' not in columns:
            cursor.execute("ALTER TABLE news ADD COLUMN analyzed_at TEXT")
            print("✓ 添加analyzed_at字段成功")
        else:
            print("⚠ analyzed_at字段已存在")
        
        # 添加analysis_type字段
        if 'analysis_type' not in columns:
            cursor.execute("ALTER TABLE news ADD COLUMN analysis_type TEXT")
            print("✓ 添加analysis_type字段成功")
        else:
            print("⚠ analysis_type字段已存在")
        
        # 提交更改
        conn.commit()
        print("\n✅ 数据库迁移完成")
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
    finally:
        if conn:
            conn.close()
            print("数据库连接已关闭")

def update_existing_records():
    """
    更新现有记录，设置默认的分析状态
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 更新已有分析结果的记录为已分析
        cursor.execute("""
            UPDATE news 
            SET is_analyzed = 1, 
                analysis_type = 'full'
            WHERE (ai_score > 0 OR summary IS NOT NULL OR keywords IS NOT NULL)
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        print(f"\n✅ 更新了 {updated_count} 条已有分析结果的记录")
        
    except Exception as e:
        print(f"❌ 更新现有记录失败: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("开始数据库迁移...")
    print(f"数据库路径: {DB_PATH}")
    print("=" * 50)
    
    migrate_database()
    update_existing_records()
    
    print("=" * 50)
    print("迁移过程完成")
