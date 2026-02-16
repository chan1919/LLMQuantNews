import aiohttp
import feedparser
from datetime import datetime
from typing import List, Dict, Any, Optional
from .base import BaseNewsCrawler, NewsItem

class RSSCrawler(BaseNewsCrawler):
    """RSS订阅源爬虫"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.feed_url = config.get('source_url', '')
        self.timeout = config.get('custom_config', {}).get('timeout', 30)
    
    @classmethod
    def get_type(cls) -> str:
        return "rss"
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """抓取RSS feed"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.feed_url, 
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
                        'Accept-Encoding': 'gzip, deflate',  # 不支持br编码
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    }
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        entries = []
                        for entry in feed.entries:
                            entry_data = {
                                'title': entry.get('title', ''),
                                'link': entry.get('link', ''),
                                'description': entry.get('description', ''),
                                'summary': entry.get('summary', ''),
                                'published': entry.get('published', ''),
                                'published_parsed': entry.get('published_parsed'),
                                'author': entry.get('author', ''),
                                'tags': [tag.term for tag in entry.get('tags', [])],
                                'source_feed': feed.feed.get('title', self.name),
                            }
                            entries.append(entry_data)
                        
                        return entries
                    else:
                        raise Exception(f"HTTP {response.status}")
        except Exception as e:
            print(f"RSS抓取失败 [{self.name}]: {e}")
            return []
    
    async def parse(self, raw_data: Dict[str, Any]) -> Optional[NewsItem]:
        """解析RSS条目"""
        try:
            # 解析发布时间
            published_at = None
            if raw_data.get('published_parsed'):
                published_at = datetime(*raw_data['published_parsed'][:6])
            elif raw_data.get('published'):
                # 尝试多种格式
                for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                    try:
                        published_at = datetime.strptime(raw_data['published'][:19], fmt)
                        break
                    except:
                        continue
            
            # 提取内容（优先使用description）
            content = raw_data.get('description', '') or raw_data.get('summary', '')
            
            return NewsItem(
                title=raw_data.get('title', '').strip(),
                url=raw_data.get('link', ''),
                content=content,
                summary=raw_data.get('summary', '')[:500] if len(content) > 500 else content,
                source=raw_data.get('source_feed', self.name),
                author=raw_data.get('author'),
                published_at=published_at,
                categories=raw_data.get('tags', []),
                metadata={'raw_entry': raw_data}
            )
        except Exception as e:
            print(f"解析RSS条目失败: {e}")
            return None

class AtomCrawler(RSSCrawler):
    """Atom feed爬虫（与RSS类似）"""
    
    @classmethod
    def get_type(cls) -> str:
        return "atom"
