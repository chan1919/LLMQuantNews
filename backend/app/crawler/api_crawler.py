import aiohttp
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from .base import BaseNewsCrawler, NewsItem

class APICrawler(BaseNewsCrawler):
    """API接口爬虫 - 用于NewsAPI、自定义API等"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = config.get('source_url', '')
        self.api_key = config.get('custom_config', {}).get('api_key', '')
        self.headers = config.get('custom_config', {}).get('headers', {})
        self.params = config.get('custom_config', {}).get('params', {})
        self.data_path = config.get('custom_config', {}).get('data_path', 'articles')
        self.timeout = config.get('custom_config', {}).get('timeout', 30)
        self.method = config.get('custom_config', {}).get('method', 'GET')
    
    @classmethod
    def get_type(cls) -> str:
        return "api"
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """调用API获取数据"""
        try:
            headers = {
                'User-Agent': 'LLMQuantBot/1.0',
                **self.headers
            }
            
            # 如果有API key，添加到headers或params
            if self.api_key:
                if 'X-API-Key' not in headers:
                    headers['X-API-Key'] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                if self.method.upper() == 'GET':
                    async with session.get(
                        self.api_url,
                        headers=headers,
                        params=self.params,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        data = await response.json()
                else:
                    async with session.post(
                        self.api_url,
                        headers=headers,
                        json=self.params,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        data = await response.json()
                
                # 根据data_path提取文章列表
                articles = data
                if self.data_path:
                    for key in self.data_path.split('.'):
                        articles = articles.get(key, [])
                
                return articles if isinstance(articles, list) else [articles]
                
        except Exception as e:
            print(f"API调用失败 [{self.name}]: {e}")
            return []
    
    async def parse(self, raw_data: Dict[str, Any]) -> Optional[NewsItem]:
        """解析API返回的数据"""
        try:
            # 从配置中获取字段映射
            field_mapping = self.custom_config.get('field_mapping', {})
            
            title_field = field_mapping.get('title', 'title')
            url_field = field_mapping.get('url', 'url')
            content_field = field_mapping.get('content', 'content')
            date_field = field_mapping.get('published_at', 'publishedAt')
            author_field = field_mapping.get('author', 'author')
            source_field = field_mapping.get('source', 'source.name')
            
            # 提取字段
            title = self._get_nested_value(raw_data, title_field)
            url = self._get_nested_value(raw_data, url_field)
            content = self._get_nested_value(raw_data, content_field, '')
            author = self._get_nested_value(raw_data, author_field)
            source = self._get_nested_value(raw_data, source_field, self.name)
            
            # 解析时间
            published_at = None
            date_str = self._get_nested_value(raw_data, date_field)
            if date_str:
                try:
                    published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    try:
                        published_at = datetime.strptime(date_str[:19], '%Y-%m-%dT%H:%M:%S')
                    except:
                        pass
            
            return NewsItem(
                title=str(title) if title else '',
                url=str(url) if url else '',
                content=str(content) if content else '',
                summary=str(content)[:500] if content else '',
                source=source or self.name,
                author=author,
                published_at=published_at,
                metadata={'raw_api_response': raw_data}
            )
        except Exception as e:
            print(f"解析API数据失败: {e}")
            return None
    
    def _get_nested_value(self, data: dict, path: str, default=None):
        """获取嵌套字典值"""
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default

class NewsAPICrawler(APICrawler):
    """NewsAPI.org 专用爬虫"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.data_path = 'articles'
        self.custom_config['field_mapping'] = {
            'title': 'title',
            'url': 'url',
            'content': 'description',
            'published_at': 'publishedAt',
            'author': 'author',
            'source': 'source.name'
        }
