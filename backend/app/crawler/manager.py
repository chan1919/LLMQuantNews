from typing import Dict, Type, Optional, List, Any
import asyncio
from datetime import datetime

from .base import BaseNewsCrawler, CrawlerType, NewsItem
from .rss_crawler import RSSCrawler, AtomCrawler
from .web_crawler import WebCrawler, SinglePageCrawler
from .api_crawler import APICrawler, NewsAPICrawler
from .custom_crawler import CustomCrawler

class CrawlerManager:
    """爬虫管理器 - 管理所有爬虫实例"""
    
    CRAWLER_MAP: Dict[str, Type[BaseNewsCrawler]] = {
        'rss': RSSCrawler,
        'atom': AtomCrawler,
        'web': WebCrawler,
        'single_page': SinglePageCrawler,
        'api': APICrawler,
        'newsapi': NewsAPICrawler,
        'custom': CustomCrawler,
    }
    
    def __init__(self):
        self._crawlers: Dict[str, BaseNewsCrawler] = {}
        self._running = False
    
    def register_crawler(self, crawler_type: str, crawler_class: Type[BaseNewsCrawler]):
        """注册新的爬虫类型"""
        self.CRAWLER_MAP[crawler_type] = crawler_class
    
    def create_crawler(self, config: Dict[str, Any]) -> Optional[BaseNewsCrawler]:
        """根据配置创建爬虫实例"""
        crawler_type = config.get('crawler_type', '').lower()
        
        if crawler_type not in self.CRAWLER_MAP:
            print(f"未知的爬虫类型: {crawler_type}")
            return None
        
        crawler_class = self.CRAWLER_MAP[crawler_type]
        try:
            crawler = crawler_class(config)
            self._crawlers[config.get('name', 'unknown')] = crawler
            return crawler
        except Exception as e:
            print(f"创建爬虫失败: {e}")
            return None
    
    async def run_crawler(self, name: str) -> List[NewsItem]:
        """运行指定爬虫"""
        crawler = self._crawlers.get(name)
        if not crawler:
            print(f"爬虫不存在: {name}")
            return []
        
        return await crawler.crawl()
    
    async def run_all(self) -> Dict[str, List[NewsItem]]:
        """运行所有爬虫"""
        results = {}
        tasks = []
        names = []
        
        for name, crawler in self._crawlers.items():
            tasks.append(crawler.crawl())
            names.append(name)
        
        if tasks:
            crawled_results = await asyncio.gather(*tasks, return_exceptions=True)
            for name, result in zip(names, crawled_results):
                if isinstance(result, Exception):
                    print(f"爬虫 [{name}] 出错: {result}")
                    results[name] = []
                else:
                    results[name] = result
        
        return results
    
    def get_crawler(self, name: str) -> Optional[BaseNewsCrawler]:
        """获取爬虫实例"""
        return self._crawlers.get(name)
    
    def list_crawlers(self) -> List[Dict[str, Any]]:
        """列出所有爬虫"""
        return [
            {
                'name': name,
                'type': crawler.get_type(),
                'config': {
                    'source_url': crawler.source_url,
                    'interval': crawler.interval,
                    'priority': crawler.priority,
                }
            }
            for name, crawler in self._crawlers.items()
        ]
    
    def remove_crawler(self, name: str) -> bool:
        """移除爬虫"""
        if name in self._crawlers:
            del self._crawlers[name]
            return True
        return False
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """获取所有可用的爬虫类型"""
        return list(cls.CRAWLER_MAP.keys())

# 全局爬虫管理器实例
crawler_manager = CrawlerManager()
