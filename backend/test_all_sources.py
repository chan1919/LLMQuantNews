#!/usr/bin/env python3
"""
批量测试所有活跃的信息源
"""
import sys
import asyncio
sys.path.insert(0, '.')

from app.crawler.rss_crawler import RSSCrawler
from app.database import SessionLocal
from app.models import CrawlerConfig

async def test_source(config):
    """测试单个信息源"""
    try:
        crawler_config = {
            'name': config.name,
            'source_url': config.source_url,
            'interval_seconds': config.interval_seconds,
            'is_active': config.is_active,
            'priority': config.priority,
            'crawler_type': config.crawler_type,
            'custom_config': config.custom_config or {}
        }
        crawler = RSSCrawler(crawler_config)
        
        raw_data = await crawler.fetch()
        
        if raw_data and len(raw_data) > 0:
            # 尝试解析第一条
            news = await crawler.parse(raw_data[0])
            if news:
                return True, len(raw_data), news.title[:40]
        return False, 0, ""
        
    except Exception as e:
        return False, 0, str(e)[:50]

async def main():
    print("="*70)
    print("批量测试所有活跃信息源")
    print("="*70)
    
    db = SessionLocal()
    configs = db.query(CrawlerConfig).filter(CrawlerConfig.is_active == True).all()
    db.close()
    
    print(f"共 {len(configs)} 个活跃信息源\n")
    
    results = []
    for i, config in enumerate(configs, 1):
        print(f"[{i}/{len(configs)}] 测试: {config.name}", end=" ")
        success, count, sample = await test_source(config)
        
        if success:
            print(f"[成功] ({count}条) - {sample}...")
            results.append((config.name, True, count))
        else:
            print(f"[失败] - {sample}")
            results.append((config.name, False, 0))
    
    # 汇总
    success_count = sum(1 for _, success, _ in results if success)
    
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)
    
    print("\n[可用的源]:")
    for name, success, count in results:
        if success:
            print(f"  [OK] {name} ({count})")
    
    print("\n[失效的源]:")
    for name, success, _ in results:
        if not success:
            print(f"  [FAIL] {name}")
    
    print(f"\n总计: {success_count}/{len(results)} 个源可用 ({success_count/len(results)*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())
    
    # 保存结果供后续处理
    print("\n建议停用的源列表:")
    for name, success, _ in results:
        if not success:
            print(f'"{name}",')
