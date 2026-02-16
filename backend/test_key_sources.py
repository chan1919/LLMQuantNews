#!/usr/bin/env python3
"""
测试关键RSS信息源的连通性和数据获取能力
"""
import sys
import asyncio
sys.path.insert(0, '.')

from app.crawler.rss_crawler import RSSCrawler
from app.database import SessionLocal
from app.models import CrawlerConfig

# 选择5个关键测试源
TEST_SOURCES = [
    "东方财富网-财经要闻",  # 国内财经权威
    "36氪-最新资讯",       # 国内科技媒体  
    "新浪财经-财经",       # 国内综合门户
    "虎嗅网-最新文章",     # 国内科技媒体
    "同花顺-财经快讯",     # 国内财经快讯
]

async def test_source(config):
    """测试单个信息源"""
    print(f"\n{'='*60}")
    print(f"测试源: {config.name}")
    print(f"类型: {config.crawler_type}")
    print(f"URL: {config.source_url}")
    print(f"{'='*60}")
    
    try:
        # 创建爬虫实例
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
        
        # 测试获取数据
        print("正在获取数据...")
        raw_data = await crawler.fetch()
        
        if not raw_data:
            print("[失败] 结果: 未能获取到数据")
            return False
        
        print(f"[成功] 获取 {len(raw_data)} 条原始数据")
        
        # 解析前3条数据
        parsed_count = 0
        print("\n解析示例（前3条）:")
        for item in raw_data[:3]:
            try:
                news = await crawler.parse(item)
                if news:
                    parsed_count += 1
                    print(f"\n  [{parsed_count}] {news.title[:50]}...")
                    print(f"      来源: {news.source}")
                    print(f"      链接: {news.url[:60]}...")
                    print(f"      时间: {news.published_at}")
            except Exception as e:
                print(f"  解析失败: {e}")
        
        print(f"\n[成功] 解析 {parsed_count}/{min(3, len(raw_data))} 条新闻")
        return parsed_count > 0
        
    except Exception as e:
        print(f"[错误] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("="*60)
    print("RSS信息源连通性测试")
    print("="*60)
    
    db = SessionLocal()
    
    # 获取测试源配置
    test_configs = []
    for source_name in TEST_SOURCES:
        config = db.query(CrawlerConfig).filter(CrawlerConfig.name == source_name).first()
        if config:
            test_configs.append(config)
        else:
            print(f"[未找到] 配置: {source_name}")
    
    db.close()
    
    print(f"\n将测试 {len(test_configs)}/{len(TEST_SOURCES)} 个信息源")
    
    # 逐个测试
    results = []
    for config in test_configs:
        success = await test_source(config)
        results.append((config.name, success))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    success_count = sum(1 for _, success in results if success)
    for name, success in results:
        status = "[正常]" if success else "[失败]"
        print(f"{status}: {name}")
    
    print(f"\n总计: {success_count}/{len(results)} 个源可用")
    
    if success_count == 0:
        print("\n[警告] 所有测试源都失败了，建议:")
        print("  1. 检查网络连接")
        print("  2. 国际源可能需要代理")
        print("  3. 部分RSS源可能已失效，需要更新URL")
    elif success_count < len(results):
        print("\n[注意] 部分源可用，建议:")
        print("  1. 修复或替换失败的源")
        print("  2. 优先使用可用的源进行数据抓取")
    else:
        print("\n[成功] 所有测试源都正常！可以开始全面抓取")

if __name__ == "__main__":
    asyncio.run(main())
