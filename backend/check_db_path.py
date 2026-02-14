#!/usr/bin/env python3
"""
检查数据库路径配置
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import engine

print("=== 数据库配置检查 ===")
print(f"DATABASE_URL: {settings.DATABASE_URL}")
print(f"Engine URL: {engine.url}")

# 检查数据库文件是否存在
db_path = str(engine.url).replace('sqlite:///', '')
print(f"数据库文件路径: {db_path}")
print(f"数据库文件存在: {os.path.exists(db_path)}")

# 检查数据库内容
import sqlite3
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM news")
total = cursor.fetchone()[0]
print(f"新闻总数: {total}")

cursor.execute("SELECT id, ai_score FROM news WHERE ai_score > 0 LIMIT 5")
results = cursor.fetchall()
print(f"有AI评分的新闻: {len(results)}")
for row in results:
    print(f"  ID: {row[0]}, AI评分: {row[1]}")

conn.close()
