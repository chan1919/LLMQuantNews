"""
数据库迁移脚本 - 添加多空影响相关字段

使用方法:
    cd backend
    python scripts/migrate_add_position_fields.py

注意：此脚本会直接修改数据库结构，请先备份数据
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config import settings

def migrate():
    """执行数据库迁移"""
    print("开始数据库迁移...")
    
    # 创建数据库连接
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("PRAGMA table_info(news)"))
        existing_columns = {row[1] for row in result.fetchall()}
        
        # News表新增字段
        news_new_fields = [
            ("position_bias", "VARCHAR(20)"),
            ("position_magnitude", "FLOAT DEFAULT 0.0"),
            ("market_impact_score", "FLOAT DEFAULT 0.0"),
            ("industry_impact_score", "FLOAT DEFAULT 0.0"),
            ("policy_impact_score", "FLOAT DEFAULT 0.0"),
            ("tech_impact_score", "FLOAT DEFAULT 0.0"),
            ("impact_analysis", "JSON"),
            ("brief_impact", "VARCHAR(500)"),
        ]
        
        print("\n1. 迁移 News 表...")
        for field_name, field_type in news_new_fields:
            if field_name not in existing_columns:
                sql = f"ALTER TABLE news ADD COLUMN {field_name} {field_type}"
                conn.execute(text(sql))
                print(f"   ✓ 添加字段: {field_name}")
            else:
                print(f"   - 字段已存在: {field_name}")
        
        # UserConfig表新增字段
        result = conn.execute(text("PRAGMA table_info(user_configs)"))
        existing_columns = {row[1] for row in result.fetchall()}
        
        user_config_new_fields = [
            ("position_sensitivity", "FLOAT DEFAULT 1.0"),
            ("keyword_positions", "JSON"),
            ("dimension_weights", "JSON"),
            ("impact_timeframe", "VARCHAR(20) DEFAULT 'medium'"),
        ]
        
        print("\n2. 迁移 UserConfig 表...")
        for field_name, field_type in user_config_new_fields:
            if field_name not in existing_columns:
                sql = f"ALTER TABLE user_configs ADD COLUMN {field_name} {field_type}"
                conn.execute(text(sql))
                print(f"   ✓ 添加字段: {field_name}")
            else:
                print(f"   - 字段已存在: {field_name}")
        
        conn.commit()
    
    print("\n✅ 数据库迁移完成！")
    print("\n注意：旧新闻数据不会自动计算多空影响，")
    print("      新爬取的新闻会自动生成这些字段。")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        sys.exit(1)
