#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库状态"""

import sys
import os

# 添加backend到路径
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_path)

from app.database import SessionLocal
from app.models import CrawlerConfig, News, PushLog

def check_database():
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("数据库状态检查")
        print("=" * 60)
        
        # 检查爬虫配置
        configs = db.query(CrawlerConfig).all()
        print(f"\n1. 信息源配置数量: {len(configs)}")
        if configs:
            for config in configs:
                status = "✓ 活跃" if config.is_active else "✗ 禁用"
                valid = "有效" if config.is_valid else ("无效" if config.is_valid is False else "未测试")
                print(f"   - {config.name} ({config.crawler_type}): {status}, {valid}")
        else:
            print("   ⚠ 没有配置信息源！")
        
        # 检查新闻数量
        news_count = db.query(News).count()
        print(f"\n2. 新闻总数: {news_count}")
        
        # 检查推送日志
        push_count = db.query(PushLog).count()
        print(f"\n3. 推送日志数: {push_count}")
        
        # 检查最近的新闻
        if news_count > 0:
            recent_news = db.query(News).order_by(News.crawled_at.desc()).limit(3).all()
            print(f"\n4. 最近3条新闻:")
            for news in recent_news:
                pushed = "已推送" if news.is_pushed else "未推送"
                print(f"   - {news.title[:50]}... [{pushed}]")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"检查出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
