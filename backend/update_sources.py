# 更新为可靠的财经RSS源
from app.database import SessionLocal
from app.models import CrawlerConfig

# 可靠的财经RSS源
real_configs = [
    {"name": "华尔街见闻", "source_url": "https://wallstreetcn.com/newsroom/global-rss", "crawler_type": "rss"},
    {"name": "证券时报网", "source_url": "https://www.stcn.com/news/rss/news.xml", "crawler_type": "rss"},
    {"name": "中国证券报", "source_url": "https://www.cs.com.cn/sszg/xwzx/03/04/rss.xml", "crawler_type": "rss"},
    {"name": "第一财经", "source_url": "https://www.yicai.com/news/rss/news.xml", "crawler_type": "rss"},
]

db = SessionLocal()

# 清除旧配置
db.query(CrawlerConfig).delete()

# 添加新配置
for config in real_configs:
    crawler_config = CrawlerConfig(
        name=config["name"],
        source_url=config["source_url"],
        crawler_type=config["crawler_type"],
        is_active=True,
        is_valid=True
    )
    db.add(crawler_config)
    print(f"添加: {config['name']}")

db.commit()
db.close()

print("\n已更新为可靠的财经RSS源！")
