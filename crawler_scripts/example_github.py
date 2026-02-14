"""
示例自定义爬虫脚本 - GitHub Trending 爬虫
演示如何爬取网页内容
"""

from app.crawler.base import BaseNewsCrawler, NewsItem
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

class GitHubTrendingCrawler(BaseNewsCrawler):
    """
    GitHub Trending 爬虫示例
    演示如何使用BeautifulSoup解析网页
    """
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """获取GitHub Trending页面"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://github.com/trending',
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 提取仓库列表
                        articles = soup.find_all('article', class_='Box-row')
                        
                        results = []
                        for article in articles:
                            # 提取仓库名
                            h2 = article.find('h2', class_='h3')
                            if h2:
                                repo_name = h2.get_text(strip=True).replace(' ', '')
                                
                                # 提取描述
                                description = ''
                                p = article.find('p', class_='col-9')
                                if p:
                                    description = p.get_text(strip=True)
                                
                                # 提取语言
                                language = ''
                                lang_span = article.find('span', itemprop='programmingLanguage')
                                if lang_span:
                                    language = lang_span.get_text(strip=True)
                                
                                # 提取star数
                                stars = ''
                                a_tags = article.find_all('a', class_='Link--muted')
                                for a in a_tags:
                                    if 'stars' in a.get('href', ''):
                                        stars = a.get_text(strip=True)
                                        break
                                
                                results.append({
                                    'repo_name': repo_name,
                                    'description': description,
                                    'language': language,
                                    'stars': stars,
                                    'url': f'https://github.com/{repo_name}'
                                })
                        
                        return results
                    else:
                        return []
        except Exception as e:
            print(f"抓取GitHub Trending失败: {e}")
            return []
    
    async def parse(self, raw_data: Dict[str, Any]) -> Optional[NewsItem]:
        """解析GitHub仓库信息"""
        try:
            title = f"GitHub Trending: {raw_data.get('repo_name', '')}"
            content = raw_data.get('description', '')
            summary = f"⭐ {raw_data.get('stars', '')} | 语言: {raw_data.get('language', 'Unknown')}"
            
            return NewsItem(
                title=title,
                url=raw_data.get('url', ''),
                content=content,
                summary=summary,
                source='GitHub Trending',
                author=raw_data.get('repo_name', '').split('/')[0] if '/' in raw_data.get('repo_name', '') else '',
                categories=['Programming', 'Open Source'],
                metadata={
                    'language': raw_data.get('language'),
                    'stars': raw_data.get('stars'),
                }
            )
        except Exception as e:
            print(f"解析失败: {e}")
            return None

# 爬虫配置
# {
#     "name": "GitHub Trending",
#     "crawler_type": "custom",
#     "source_url": "https://github.com/trending",
#     "interval_seconds": 3600,
#     "priority": 5,
#     "custom_script": "<上面的代码>"
# }
