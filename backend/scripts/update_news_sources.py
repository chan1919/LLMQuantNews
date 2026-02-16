#!/usr/bin/env python3
"""
优化版新闻信息源配置 - 优先使用国内可用且稳定的RSS源
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import engine, Base
from app.models import CrawlerConfig

# 优化的信息源配置 - 经过测试验证的可靠源
news_sources = [
    # ===== 国内财经（高优先级）=====
    {
        "name": "新浪财经-财经",
        "crawler_type": "rss",
        "source_url": "http://rss.sina.com.cn/news/finance/yaowen.xml",
        "interval_seconds": 300,
        "priority": 6,
        "is_active": True
    },
    {
        "name": "东方财富网-财经要闻",
        "crawler_type": "rss", 
        "source_url": "http://rss.eastmoney.com/rss_news.xml",
        "interval_seconds": 300,
        "priority": 6,
        "is_active": True
    },
    {
        "name": "东方财富网-股票资讯",
        "crawler_type": "rss",
        "source_url": "http://rss.eastmoney.com/rss_stock.xml",
        "interval_seconds": 300,
        "priority": 6,
        "is_active": True
    },
    {
        "name": "同花顺-财经快讯",
        "crawler_type": "rss",
        "source_url": "http://feed.10jqka.com.cn/feed/toutiao.xml",
        "interval_seconds": 300,
        "priority": 6,
        "is_active": True
    },
    {
        "name": "网易新闻-财经",
        "crawler_type": "rss",
        "source_url": "http://money.163.com/special/00251G6B/rss.xml",
        "interval_seconds": 300,
        "priority": 6,
        "is_active": True
    },
    {
        "name": "腾讯新闻-财经",
        "crawler_type": "rss",
        "source_url": "http://finance.qq.com/caijingzhiku/rss_caijingzhiku.xml",
        "interval_seconds": 300,
        "priority": 6,
        "is_active": True
    },
    
    # ===== 国内科技 =====
    {
        "name": "36氪-最新资讯",
        "crawler_type": "rss",
        "source_url": "http://www.36kr.com/feed",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "虎嗅网-最新文章",
        "crawler_type": "rss",
        "source_url": "http://www.huxiu.com/rss/0.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "爱范儿-最新文章",
        "crawler_type": "rss",
        "source_url": "http://www.ifanr.com/feed",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "极客公园-最新文章",
        "crawler_type": "rss",
        "source_url": "http://www.geekpark.net/rss",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    
    # ===== 国内综合新闻 =====
    {
        "name": "新浪财经-国内",
        "crawler_type": "rss",
        "source_url": "http://rss.sina.com.cn/news/marquee/ddt.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "新浪财经-科技",
        "crawler_type": "rss",
        "source_url": "http://rss.sina.com.cn/news/tech/internet.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "网易新闻-科技",
        "crawler_type": "rss",
        "source_url": "http://tech.163.com/special/000940VM/rss.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "中国新闻网-国内",
        "crawler_type": "rss",
        "source_url": "http://www.chinanews.com.cn/rss/scroll-news.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "中国新闻网-财经",
        "crawler_type": "rss",
        "source_url": "http://www.chinanews.com.cn/rss/finance.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    
    # ===== 国际新闻（可能需要代理）=====
    {
        "name": "BBC News-头条新闻",
        "crawler_type": "rss",
        "source_url": "http://feeds.bbci.co.uk/news/rss.xml",
        "interval_seconds": 600,
        "priority": 4,
        "is_active": True  # 可以尝试，如果失败则停用
    },
    {
        "name": "Reuters-头条新闻",
        "crawler_type": "rss",
        "source_url": "http://feeds.reuters.com/reuters/topNews",
        "interval_seconds": 600,
        "priority": 4,
        "is_active": True
    },
    {
        "name": "TechCrunch-最新文章",
        "crawler_type": "rss",
        "source_url": "https://techcrunch.com/feed/",
        "interval_seconds": 600,
        "priority": 4,
        "is_active": True
    },
    {
        "name": "The Verge-最新文章",
        "crawler_type": "rss",
        "source_url": "https://www.theverge.com/rss/index.xml",
        "interval_seconds": 600,
        "priority": 4,
        "is_active": True
    },
]

def update_news_sources():
    """更新新闻信息源配置"""
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 停用失效的源（雪球）
        disabled_sources = ['雪球-热门股票', '雪球-财经要闻']
        for source_name in disabled_sources:
            config = db.query(CrawlerConfig).filter(CrawlerConfig.name == source_name).first()
            if config:
                config.is_active = False
                print(f"已停用失效源: {source_name}")
        
        # 添加新的源
        existing_names = {c.name for c in db.query(CrawlerConfig).all()}
        added_count = 0
        
        for source in news_sources:
            if source['name'] in existing_names:
                # 更新现有配置
                config = db.query(CrawlerConfig).filter(CrawlerConfig.name == source['name']).first()
                config.source_url = source['source_url']
                config.interval_seconds = source['interval_seconds']
                config.priority = source['priority']
                config.is_active = source['is_active']
                print(f"更新配置: {source['name']}")
            else:
                # 创建新配置
                config = CrawlerConfig(
                    name=source['name'],
                    crawler_type=source['crawler_type'],
                    source_url=source['source_url'],
                    interval_seconds=source['interval_seconds'],
                    priority=source['priority'],
                    is_active=source['is_active']
                )
                db.add(config)
                added_count += 1
                print(f"添加配置: {source['name']}")
        
        db.commit()
        print(f"\n更新完成！")
        print(f"新增配置: {added_count}")
        
        # 统计
        total = db.query(CrawlerConfig).count()
        active = db.query(CrawlerConfig).filter(CrawlerConfig.is_active == True).count()
        print(f"总配置数: {total}")
        print(f"活跃配置: {active}")
        
    except Exception as e:
        print(f"更新失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_news_sources()
