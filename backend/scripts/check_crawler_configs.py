#!/usr/bin/env python3
"""
检查爬虫配置并启动爬虫服务
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import CrawlerConfig
from app.crawler.manager import crawler_manager
import asyncio

async def main():
    """检查爬虫配置并启动爬虫服务"""
    print("检查爬虫配置...")

    # 获取数据库会话
    db = SessionLocal()

    try:
        # 获取所有爬虫配置
        configs = db.query(CrawlerConfig).all()
        print(f"发现 {len(configs)} 个爬虫配置")

        # 打印活跃的爬虫配置
        active_configs = db.query(CrawlerConfig).filter(CrawlerConfig.is_active == True).all()
        print(f"活跃的爬虫配置: {len(active_configs)}")

        for config in active_configs:
            print(f"  - {config.name} ({config.crawler_type})")

        # 为每个活跃的配置创建爬虫实例
        print("\n创建爬虫实例...")
        for config in active_configs:
            config_dict = config.to_dict()
            crawler_manager.create_crawler(config_dict)

        print(f"已创建 {len(crawler_manager._crawlers)} 个爬虫实例")

        # 运行所有爬虫
        print("\n运行所有爬虫...")
        results = await crawler_manager.run_all()
        print("爬虫运行完成")

        # 统计结果
        total_news = 0
        for name, items in results.items():
            print(f"{name}: 抓取到 {len(items)} 条新闻")
            total_news += len(items)

        print(f"\n总抓取新闻数: {total_news}")

        # 保存新闻到数据库
        print("\n保存新闻到数据库...")
        from app.models import News
        from app.schemas import NewsCreate

        saved_count = 0
        batch_size = 100
        batch_count = 0

        # 先收集所有不重复的URL
        all_urls = set()
        for name, items in results.items():
            for item in items:
                all_urls.add(item.url)

        print(f"去重后新闻数: {len(all_urls)}")

        # 检查数据库中已存在的URL
        existing_urls = set()
        existing_news = db.query(News.url).all()
        for news in existing_news:
            existing_urls.add(news.url)

        # 计算需要保存的新闻数
        new_urls = all_urls - existing_urls
        print(f"需要保存的新闻数: {len(new_urls)}")

        # 保存新的新闻
        for name, items in results.items():
            # 获取爬虫类型
            crawler = crawler_manager.get_crawler(name)
            source_type = crawler.get_type() if crawler else 'unknown'

            for item in items:
                # 检查是否是新的URL
                if item.url not in new_urls:
                    continue

                # 从new_urls中移除，避免重复处理
                new_urls.remove(item.url)

                # 创建新闻记录
                news_data = NewsCreate(
                    title=item.title,
                    content=item.content,
                    url=item.url,
                    source=name,
                    source_type=source_type,
                    author=item.author,
                    published_at=item.published_at
                )

                # 保存到数据库
                try:
                    news = News(**news_data.model_dump())
                    db.add(news)
                    saved_count += 1
                    batch_count += 1

                    # 每batch_size条提交一次
                    if batch_count >= batch_size:
                        db.commit()
                        print(f"已提交 {saved_count} 条新闻")
                        batch_count = 0
                except Exception as e:
                    print(f"保存新闻失败: {e}")
                    db.rollback()

        # 提交剩余的新闻
        if batch_count > 0:
            db.commit()
            print(f"已提交剩余 {batch_count} 条新闻")

        print(f"\n已保存 {saved_count} 条新闻到数据库")

        # 再次检查新闻数量
        news_count = db.query(News).count()
        print(f"\n数据库中新闻数量: {news_count}")

    finally:
        # 关闭数据库会话
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
