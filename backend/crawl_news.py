# 直接爬取新闻
import asyncio
from app.database import SessionLocal
from app.models import CrawlerConfig, News
from app.crawler import crawler_manager

async def crawl_news():
    db = SessionLocal()
    
    # 获取活跃的配置
    configs = db.query(CrawlerConfig).filter(CrawlerConfig.is_active == True).all()
    print(f"找到 {len(configs)} 个活跃爬虫配置")
    
    total_news = 0
    
    for config in configs:
        print(f"\n正在爬取: {config.name}")
        
        try:
            # 创建爬虫
            crawler = crawler_manager.create_crawler(config.to_dict())
            if not crawler:
                print(f"  创建爬虫失败")
                continue
            
            # 执行爬取
            news_items = await crawler.crawl()
            print(f"  爬取到 {len(news_items)} 条新闻")
            
            # 保存到数据库
            for item in news_items:
                # 处理NewsItem对象或字典
                if hasattr(item, 'title'):
                    # 是NewsItem对象
                    title = item.title
                    content = item.content
                    url = item.url
                    published_at = getattr(item, 'published_at', None)
                else:
                    # 是字典
                    title = item.get('title', '')
                    content = item.get('content', '')
                    url = item.get('url', '')
                    published_at = item.get('published_at')
                
                if not title:
                    continue
                
                # 检查是否已存在
                if url:
                    existing = db.query(News).filter(News.url == url).first()
                    if existing:
                        continue
                
                news = News(
                    title=title,
                    content=content or '',
                    url=url or '',
                    source=config.name,
                    source_type=config.crawler_type,
                    published_at=published_at,
                    crawled_at=published_at,
                    is_analyzed=False,
                    is_pushed=False,
                )
                db.add(news)
                total_news += 1
            
            db.commit()
            print(f"  新增 {total_news} 条新闻")
            
        except Exception as e:
            print(f"  爬取失败: {e}")
            import traceback
            traceback.print_exc()
    
    db.close()
    print(f"\n总共新增 {total_news} 条新闻")

if __name__ == "__main__":
    asyncio.run(crawl_news())
