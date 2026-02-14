#!/usr/bin/env python3
"""
添加测试新闻信息源配置到数据库
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import engine, Base
from app.models import CrawlerConfig

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 测试信息源配置列表
test_news_sources = [
    # 有效的测试信息源
    {
        "name": "测试-RSS-有效",
        "crawler_type": "rss",
        "source_url": "http://rss.sina.com.cn/news/marquee/ddt.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "测试-RSS-有效2",
        "crawler_type": "rss",
        "source_url": "https://techcrunch.com/feed/",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "测试-Web-有效",
        "crawler_type": "web",
        "source_url": "https://www.example.com",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "测试-API-有效",
        "crawler_type": "api",
        "source_url": "https://api.github.com/users/octocat",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    
    # 无效的测试信息源
    {
        "name": "测试-RSS-无效-404",
        "crawler_type": "rss",
        "source_url": "http://example.com/nonexistent/rss.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "测试-RSS-无效-非RSS",
        "crawler_type": "rss",
        "source_url": "https://www.example.com",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "测试-Web-无效-404",
        "crawler_type": "web",
        "source_url": "http://example.com/nonexistent",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "测试-API-无效-404",
        "crawler_type": "api",
        "source_url": "https://api.github.com/nonexistent/endpoint",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    
    # 自定义爬虫测试
    {
        "name": "测试-自定义-有效",
        "crawler_type": "custom",
        "source_url": "https://www.example.com",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True,
        "custom_script": """def crawl():
    return [{
        'title': '测试新闻',
        'content': '这是一条测试新闻内容',
        'url': 'https://www.example.com/test',
        'published_at': '2024-01-01T00:00:00Z'
    }]"""
    },
    {
        "name": "测试-自定义-无效-脚本空",
        "crawler_type": "custom",
        "source_url": "https://www.example.com",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True,
        "custom_script": ""
    }
]

def add_test_news_sources():
    """添加测试新闻信息源到数据库"""
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 检查是否已存在配置
        existing_configs = db.query(CrawlerConfig).all()
        existing_names = {config.name for config in existing_configs}

        added_count = 0
        skipped_count = 0

        for source in test_news_sources:
            if source['name'] in existing_names:
                print(f"跳过已存在的测试配置: {source['name']}")
                skipped_count += 1
                continue

            # 创建新的配置
            config = CrawlerConfig(
                name=source['name'],
                crawler_type=source['crawler_type'],
                source_url=source['source_url'],
                interval_seconds=source['interval_seconds'],
                priority=source['priority'],
                is_active=source['is_active'],
                custom_script=source.get('custom_script')
            )

            db.add(config)
            added_count += 1
            print(f"添加测试配置: {source['name']}")

        # 提交更改
        db.commit()

        print(f"\n添加完成！")
        print(f"新增测试配置: {added_count}")
        print(f"跳过配置: {skipped_count}")
        print(f"总配置数: {added_count + len(existing_configs)}")

    except Exception as e:
        print(f"添加失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_news_sources()
