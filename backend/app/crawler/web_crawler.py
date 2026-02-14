import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from newspaper import Article
import asyncio

from .base import BaseNewsCrawler, NewsItem

class WebCrawler(BaseNewsCrawler):
    """网页爬虫 - 使用newspaper4k提取内容"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.list_url = config.get('source_url', '')
        self.article_selector = config.get('custom_config', {}).get('article_selector', 'a')
        self.timeout = config.get('custom_config', {}).get('timeout', 30)
        self.max_articles = config.get('custom_config', {}).get('max_articles', 10)
        self.language = config.get('custom_config', {}).get('language', 'zh')
    
    @classmethod
    def get_type(cls) -> str:
        return "web"
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """抓取文章列表页"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.list_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 提取文章链接
                        articles = []
                        links = soup.select(self.article_selector)[:self.max_articles]
                        
                        for link in links:
                            href = link.get('href', '')
                            if href:
                                full_url = urljoin(self.list_url, href)
                                articles.append({
                                    'url': full_url,
                                    'title': link.get_text(strip=True),
                                    'list_page_html': html,
                                })
                        
                        return articles
                    else:
                        raise Exception(f"HTTP {response.status}")
        except Exception as e:
            print(f"网页抓取失败 [{self.name}]: {e}")
            return []
    
    async def parse(self, raw_data: Dict[str, Any]) -> Optional[NewsItem]:
        """使用newspaper4k解析文章"""
        try:
            url = raw_data.get('url', '')
            
            # 使用newspaper4k提取文章
            article = Article(url, language=self.language)
            
            # 下载和解析（newspaper是同步的，在线程池中运行）
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, article.download)
            await loop.run_in_executor(None, article.parse)
            
            # NLP处理（可选，比较耗时）
            # await loop.run_in_executor(None, article.nlp)
            
            if not article.title:
                return None
            
            # 提取发布时间
            published_at = None
            if article.publish_date:
                published_at = article.publish_date
            
            return NewsItem(
                title=article.title.strip(),
                url=url,
                content=article.text,
                summary=article.summary or article.text[:500] if article.text else '',
                source=self.name,
                author=article.authors[0] if article.authors else None,
                published_at=published_at,
                categories=list(article.tags) if article.tags else [],
                metadata={
                    'top_image': article.top_image,
                    'movies': article.movies,
                    'raw_html': article.html[:10000] if article.html else None,
                }
            )
        except Exception as e:
            print(f"解析网页文章失败 [{raw_data.get('url', '')}]: {e}")
            return None

class SinglePageCrawler(WebCrawler):
    """单页爬虫 - 直接爬取单个URL"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """直接返回单个URL"""
        return [{'url': self.list_url}]
