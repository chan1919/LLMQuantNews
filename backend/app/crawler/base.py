from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CrawlerType(str, Enum):
    RSS = "rss"
    WEB = "web"
    API = "api"
    CUSTOM = "custom"

@dataclass
class NewsItem:
    """新闻数据模型"""
    title: str
    url: str
    content: Optional[str] = None
    summary: Optional[str] = None
    source: str = ""
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    categories: List[str] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

class BaseNewsCrawler(ABC):
    """爬虫基类 - 所有爬虫必须继承"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', self.__class__.__name__)
        self.source_url = config.get('source_url', '')
        self.interval = config.get('interval_seconds', 300)
        self.priority = config.get('priority', 5)
        self.custom_config = config.get('custom_config', {})
    
    @abstractmethod
    async def fetch(self) -> List[Dict[str, Any]]:
        """
        抓取原始数据
        返回原始数据列表
        """
        pass
    
    @abstractmethod
    async def parse(self, raw_data: Dict[str, Any]) -> Optional[NewsItem]:
        """
        解析单条原始数据为NewsItem
        返回None表示解析失败或数据无效
        """
        pass
    
    async def crawl(self) -> List[NewsItem]:
        """
        执行完整爬取流程
        """
        try:
            raw_items = await self.fetch()
            news_items = []
            
            for raw_data in raw_items:
                try:
                    item = await self.parse(raw_data)
                    if item and self._validate(item):
                        news_items.append(item)
                except Exception as e:
                    print(f"解析失败: {e}")
                    continue
            
            return news_items
        except Exception as e:
            print(f"爬取失败 [{self.name}]: {e}")
            return []
    
    def _validate(self, item: NewsItem) -> bool:
        """验证新闻有效性"""
        if not item.title or len(item.title.strip()) < 5:
            return False
        if not item.url or not item.url.startswith('http'):
            return False
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取爬虫统计信息"""
        return {
            'name': self.name,
            'type': self.get_type(),
            'source_url': self.source_url,
            'interval': self.interval,
            'priority': self.priority,
        }
    
    @classmethod
    def get_type(cls) -> str:
        """返回爬虫类型标识"""
        return "base"
