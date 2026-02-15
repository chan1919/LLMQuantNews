# 更新为真正的财经RSS源
from app.database import SessionLocal
from app.models import CrawlerConfig

# 真正的财经RSS源
real_configs = [
    {"name": "华尔街见闻-主要", "source_url": "https://wallstreetcn.com/newsroom/global-rss", "crawler_type": "rss"},
    {"name": "新浪财经-股市", "source_url": "https://finance.sina.com.cn/roll/index_roll.shtml#pagevar", "crawler_type": "web"},
    {"name": "网易财经", "source_url": "https://money.163.com/", "crawler_type": "web"},
    {"name": "凤凰网财经", "source_url": "https://finance.ifeng.com/", "crawler_type": "web"},
    {"name": "东方财富网", "source_url": "https://www.eastmoney.com/", "crawler_type": "web"},
    {"name": "同花顺财经", "source_url": "https://www.10jqka.com.cn/", "crawler_type": "web"},
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

print("\n已更新为真正的财经RSS源！")
