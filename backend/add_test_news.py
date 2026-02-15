# 添加测试新闻数据
from app.database import SessionLocal
from app.models import News
from datetime import datetime, timedelta

# 测试新闻数据 - 使用唯一URL
test_news = [
    {
        "title": "A股市场今日大涨 沪指突破3400点关口",
        "content": "今日A股市场全线上涨，沪指突破3400点整数关口，深成指涨幅超过2%。市场成交额突破1.2万亿元，北向资金净流入超过50亿元。分析师认为，政策利好和业绩预期提升是上涨主要驱动力。",
        "source": "新浪财经",
        "source_type": "rss",
        "url": "https://finance.sina.com.cn/stock/1",
    },
    {
        "title": "央行降准释放流动性 利好金融市场",
        "content": "中国人民银行宣布降准0.5个百分点，预计释放长期流动性约1万亿元。此举旨在支持实体经济发展，降低融资成本。业内人士表示，降准对股市、债市均构成利好。",
        "source": "网易财经",
        "source_type": "rss",
        "url": "https://money.163.com/2",
    },
    {
        "title": "人工智能领域再获突破 AI芯片需求激增",
        "content": "最新研究显示，人工智能技术在多个领域取得新突破，AI芯片市场需求持续攀升。多家科技巨头加大研发投入，产业链上下游企业迎来发展机遇。",
        "source": "腾讯财经",
        "source_type": "web",
        "url": "https://finance.qq.com/3",
    },
    {
        "title": "新能源车销量创新高 产业链公司业绩预增",
        "content": "最新数据显示，上月新能源汽车销量同比增长超过80%，创历史新高。比亚迪、宁德时代等龙头企业业绩预告大幅增长，行业景气度持续攀升。",
        "source": "华尔街见闻",
        "source_type": "web",
        "url": "https://wallstreetcn.com/4",
    },
    {
        "title": "半导体国产化加速 芯片板块集体上涨",
        "content": "随着国产替代进程加速，半导体板块今日集体大涨。多家国内芯片厂商发布新品，技术突破消息频传。机构看好半导体行业的长期发展前景。",
        "source": "新浪财经",
        "source_type": "rss",
        "url": "https://finance.sina.com.cn/5",
    },
    {
        "title": "房地产政策持续松绑 板块估值修复",
        "content": "多地出台房地产松绑政策，行业板块估值迎来修复。分析师认为，政策底部已经显现，优质地产股具备配置价值。",
        "source": "网易财经",
        "source_type": "web",
        "url": "https://money.163.com/6",
    },
    {
        "title": "5G建设加速推进 通信设备商受益",
        "content": "运营商5G基站建设加速，通信设备商订单饱满。华为、中兴等企业业绩表现亮眼，产业链发展势头强劲。",
        "source": "腾讯财经",
        "source_type": "web",
        "url": "https://finance.qq.com/7",
    },
    {
        "title": "医药板块估值回调 创新药企受关注",
        "content": "医药板块经过前期调整，估值已处于历史低位。创新药企研发进展顺利，多款新药即将上市，投资价值凸显。",
        "source": "新浪财经",
        "source_type": "rss",
        "url": "https://finance.sina.com.cn/8",
    },
]

db = SessionLocal()

# 检查现有新闻数
existing_count = db.query(News).count()
print(f"现有新闻数: {existing_count}")

# 添加新闻
for i, news_data in enumerate(test_news):
    # 检查是否已存在
    existing = db.query(News).filter(News.url == news_data["url"]).first()
    if existing:
        print(f"已存在: {news_data['title'][:30]}...")
        continue
        
    news = News(
        title=news_data["title"],
        content=news_data["content"],
        source=news_data["source"],
        source_type=news_data["source_type"],
        url=news_data["url"],
        crawled_at=datetime.utcnow() - timedelta(minutes=i*10),
        published_at=datetime.utcnow() - timedelta(minutes=i*10),
        is_analyzed=False,
        is_pushed=False,
    )
    db.add(news)
    print(f"添加: {news_data['title'][:30]}...")

db.commit()

# 检查最终数量
final_count = db.query(News).count()
print(f"\n最终新闻数: {final_count}")
db.close()
