#!/usr/bin/env python3
"""
添加新闻信息源配置到数据库
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import engine, Base
from app.models import CrawlerConfig

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 信息源配置列表
news_sources = [
    # 国内新闻
    {
        "name": "新浪新闻-国内",
        "crawler_type": "rss",
        "source_url": "http://rss.sina.com.cn/news/marquee/ddt.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "新浪新闻-财经",
        "crawler_type": "rss",
        "source_url": "http://rss.sina.com.cn/news/finance/yaowen.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "新浪新闻-科技",
        "crawler_type": "rss",
        "source_url": "http://rss.sina.com.cn/news/tech/internet.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "网易新闻-新闻中心",
        "crawler_type": "rss",
        "source_url": "http://news.163.com/special/00011K6L/rss_newstop.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "网易新闻-财经",
        "crawler_type": "rss",
        "source_url": "http://money.163.com/special/00251G6B/rss.xml",
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
        "name": "腾讯新闻-新闻中心",
        "crawler_type": "rss",
        "source_url": "http://news.qq.com/newsgn/rss_newsgn.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "腾讯新闻-财经",
        "crawler_type": "rss",
        "source_url": "http://finance.qq.com/caijingzhiku/rss_caijingzhiku.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "腾讯新闻-科技",
        "crawler_type": "rss",
        "source_url": "http://tech.qq.com/mobile/rss_mobile.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "央视新闻",
        "crawler_type": "rss",
        "source_url": "http://www.cctv.com/rss/index.xml",
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
        "name": "中国新闻网-国际",
        "crawler_type": "rss",
        "source_url": "http://www.chinanews.com.cn/rss/world.xml",
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

    # 国内财经
    {
        "name": "雪球-热门股票",
        "crawler_type": "rss",
        "source_url": "https://xueqiu.com/statuses/hot.xml",
        "interval_seconds": 300,
        "priority": 6,
        "is_active": True
    },
    {
        "name": "雪球-财经要闻",
        "crawler_type": "rss",
        "source_url": "https://xueqiu.com/statuses/finance.xml",
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

    # 国内科技
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

    # 国外新闻
    {
        "name": "Reuters-头条新闻",
        "crawler_type": "rss",
        "source_url": "http://feeds.reuters.com/reuters/topNews",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "Reuters-财经新闻",
        "crawler_type": "rss",
        "source_url": "http://feeds.reuters.com/reuters/businessNews",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "Reuters-科技新闻",
        "crawler_type": "rss",
        "source_url": "http://feeds.reuters.com/reuters/technologyNews",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "Bloomberg-头条新闻",
        "crawler_type": "rss",
        "source_url": "https://www.bloomberg.com/feeds/bbiz/latest.rss",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "Bloomberg-市场新闻",
        "crawler_type": "rss",
        "source_url": "https://www.bloomberg.com/feeds/markets/latest.rss",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "CNBC-头条新闻",
        "crawler_type": "rss",
        "source_url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "CNBC-市场新闻",
        "crawler_type": "rss",
        "source_url": "https://www.cnbc.com/id/15839135/device/rss/rss.html",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "BBC News-头条新闻",
        "crawler_type": "rss",
        "source_url": "http://feeds.bbci.co.uk/news/rss.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "BBC News-世界新闻",
        "crawler_type": "rss",
        "source_url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "The Guardian-头条新闻",
        "crawler_type": "rss",
        "source_url": "https://www.theguardian.com/world/rss",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "The Guardian-财经新闻",
        "crawler_type": "rss",
        "source_url": "https://www.theguardian.com/business/rss",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },

    # 国外财经
    {
        "name": "Financial Times-市场新闻",
        "crawler_type": "rss",
        "source_url": "https://www.ft.com/rss/markets",
        "interval_seconds": 300,
        "priority": 6,
        "is_active": True
    },
    {
        "name": "Yahoo Finance-市场概览",
        "crawler_type": "rss",
        "source_url": "https://finance.yahoo.com/news/rssindex",
        "interval_seconds": 300,
        "priority": 6,
        "is_active": True
    },
    {
        "name": "Investing.com-市场新闻",
        "crawler_type": "rss",
        "source_url": "https://www.investing.com/rss/news.rss",
        "interval_seconds": 300,
        "priority": 6,
        "is_active": True
    },
    {
        "name": "Investing.com-经济日历",
        "crawler_type": "rss",
        "source_url": "https://www.investing.com/rss/economicCalendar.rss",
        "interval_seconds": 300,
        "priority": 6,
        "is_active": True
    },

    # 国外科技
    {
        "name": "TechCrunch-最新文章",
        "crawler_type": "rss",
        "source_url": "https://techcrunch.com/feed/",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "Wired-最新文章",
        "crawler_type": "rss",
        "source_url": "https://www.wired.com/feed/rss",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "The Verge-最新文章",
        "crawler_type": "rss",
        "source_url": "https://www.theverge.com/rss/index.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    },
    {
        "name": "Engadget-最新文章",
        "crawler_type": "rss",
        "source_url": "https://www.engadget.com/rss.xml",
        "interval_seconds": 300,
        "priority": 5,
        "is_active": True
    }
]

def add_news_sources():
    """添加新闻信息源到数据库"""
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 检查是否已存在配置
        existing_configs = db.query(CrawlerConfig).all()
        existing_names = {config.name for config in existing_configs}

        added_count = 0
        skipped_count = 0

        for source in news_sources:
            if source['name'] in existing_names:
                print(f"跳过已存在的配置: {source['name']}")
                skipped_count += 1
                continue

            # 创建新的配置
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

        # 提交更改
        db.commit()

        print(f"\n添加完成！")
        print(f"新增配置: {added_count}")
        print(f"跳过配置: {skipped_count}")
        print(f"总配置数: {added_count + len(existing_configs)}")

    except Exception as e:
        print(f"添加失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_news_sources()
