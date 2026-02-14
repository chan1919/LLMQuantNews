"""
示例自定义爬虫脚本 - Hacker News热榜爬虫
这个脚本演示了如何编写自定义爬虫
"""

from app.crawler.base import BaseNewsCrawler, NewsItem
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional

class HackerNewsCrawler(BaseNewsCrawler):
    """
    Hacker News 热榜爬虫示例
    演示如何抓取API接口并解析数据
    """
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """获取Hacker News热榜"""
        try:
            async with aiohttp.ClientSession() as session:
                # 获取前30个热门故事ID
                async with session.get(
                    'https://hacker-news.firebaseio.com/v0/topstories.json'
                ) as response:
                    if response.status == 200:
                        story_ids = await response.json()
                        # 只取前10个
                        story_ids = story_ids[:10]
                        
                        stories = []
                        for story_id in story_ids:
                            # 获取每个故事的详情
                            async with session.get(
                                f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                            ) as story_response:
                                if story_response.status == 200:
                                    story = await story_response.json()
                                    if story and story.get('title'):
                                        stories.append(story)
                        
                        return stories
                    else:
                        return []
        except Exception as e:
            print(f"抓取Hacker News失败: {e}")
            return []
    
    async def parse(self, raw_data: Dict[str, Any]) -> Optional[NewsItem]:
        """解析Hacker News条目"""
        try:
            # 提取时间戳
            timestamp = raw_data.get('time', 0)
            published_at = datetime.fromtimestamp(timestamp) if timestamp else datetime.utcnow()
            
            # 构建URL
            if raw_data.get('url'):
                url = raw_data['url']
            else:
                # 如果是Ask HN等没有外部链接的
                url = f"https://news.ycombinator.com/item?id={raw_data.get('id')}"
            
            return NewsItem(
                title=raw_data.get('title', ''),
                url=url,
                content='',  # HN API不提供全文
                summary=f"Score: {raw_data.get('score', 0)} | Comments: {raw_data.get('descendants', 0)}",
                source='Hacker News',
                author=raw_data.get('by', ''),
                published_at=published_at,
                categories=['Tech', 'Programming'],
                metadata={
                    'score': raw_data.get('score'),
                    'comments': raw_data.get('descendants'),
                    'story_id': raw_data.get('id'),
                }
            )
        except Exception as e:
            print(f"解析失败: {e}")
            return None

# 爬虫配置
# {
#     "name": "Hacker News 热榜",
#     "crawler_type": "custom",
#     "source_url": "https://news.ycombinator.com",
#     "interval_seconds": 300,
#     "priority": 5,
#     "custom_script": "<上面的代码>"
# }
