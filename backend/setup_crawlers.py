# 添加默认爬虫配置
from app.database import SessionLocal
from app.models import CrawlerConfig

# 默认RSS源
default_configs = [
    {"name": "新浪财经", "source_url": "https://finance.sina.com.cn/service/iframe.shtml?_=0.123456789", "crawler_type": "rss"},
    {"name": "网易财经", "source_url": "https://money.163.com/", "crawler_type": "web"},
    {"name": "腾讯财经", "source_url": "https://finance.qq.com/", "crawler_type": "web"},
    {"name": "华尔街见闻", "source_url": "https://api.xuetangx.com/", "crawler_type": "web"},
]

db = SessionLocal()

# 添加配置
for config in default_configs:
    existing = db.query(CrawlerConfig).filter(CrawlerConfig.name == config["name"]).first()
    if not existing:
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

print("爬虫配置完成！")
