#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试消息去重功能
"""

from app.database import SessionLocal
from app.models import News
from datetime import datetime, timedelta


def test_duplicate_removal():
    """测试消息去重功能"""
    db = SessionLocal()
    
    try:
        # 创建测试新闻
        test_news = News(
            title="测试新闻标题",
            content="这是一条测试新闻内容，用于测试消息去重功能。",
            url="https://example.com/test-news-1",
            source="测试源",
            source_type="test",
            author="测试作者",
            published_at=datetime.utcnow(),
            crawled_at=datetime.utcnow(),
            is_analyzed=True
        )
        db.add(test_news)
        db.commit()
        print(f"创建测试新闻成功: {test_news.title}")
        
        # 测试URL去重
        duplicate_url_news = News(
            title="不同标题的新闻",
            content="不同的内容",
            url="https://example.com/test-news-1",  # 相同的URL
            source="测试源",
            source_type="test",
            author="测试作者",
            published_at=datetime.utcnow(),
            crawled_at=datetime.utcnow()
        )
        
        # 检查是否已存在
        existing_by_url = db.query(News).filter(News.url == duplicate_url_news.url).first()
        if existing_by_url:
            print("✅ URL去重测试成功: 发现重复的URL")
        else:
            print("❌ URL去重测试失败: 未发现重复的URL")
        
        # 测试内容去重
        duplicate_content_news = News(
            title="测试新闻标题",  # 相同的标题
            content="这是一条测试新闻内容，用于测试消息去重功能。",  # 相同的内容
            url="https://example.com/test-news-2",  # 不同的URL
            source="测试源",
            source_type="test",
            author="测试作者",
            published_at=datetime.utcnow(),
            crawled_at=datetime.utcnow()
        )
        
        # 检查是否已存在
        from sqlalchemy import or_
        existing_by_content = db.query(News).filter(
            or_(
                News.title == duplicate_content_news.title,
                News.content == duplicate_content_news.content
            ),
            News.crawled_at >= datetime.utcnow() - timedelta(days=1)
        ).first()
        
        if existing_by_content:
            print("✅ 内容去重测试成功: 发现重复的内容")
        else:
            print("❌ 内容去重测试失败: 未发现重复的内容")
        
        # 清理测试数据
        db.delete(test_news)
        db.commit()
        print("测试完成，清理数据成功")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_duplicate_removal()
