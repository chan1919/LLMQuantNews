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
    all_urls = set()  # 用于跨源去重
    
    # 先获取所有已存在的URL
    existing_urls = {row[0] for row in db.query(News.url).all() if row[0]}
    all_urls.update(existing_urls)
    print(f"数据库中已有 {len(existing_urls)} 条新闻")
    
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
            
            added_count = 0
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
                
                # 去重检查
                if url and url in all_urls:
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
                if url:
                    all_urls.add(url)
                added_count += 1
                total_news += 1
            
            db.commit()
            print(f"  新增 {added_count} 条新闻")
            
        except Exception as e:
            print(f"  爬取失败: {e}")
            db.rollback()  # 回滚当前批次
            import traceback
            traceback.print_exc()
    
    db.close()
    print(f"\n总共新增 {total_news} 条新闻")

if __name__ == "__main__":
    asyncio.run(crawl_news())
