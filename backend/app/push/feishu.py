import lark
from lark import Lark
from datetime import datetime
from typing import Dict, Any

from .base import BasePusher, PushResult
from app.config import settings

class FeishuPusher(BasePusher):
    """飞书消息推送"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config.get('app_id') or settings.FEISHU_APP_ID
        self.app_secret = config.get('app_secret') or settings.FEISHU_APP_SECRET
        self.webhook = config.get('webhook')
        self.chat_id = config.get('chat_id')
        self._client = None
    
    def _get_client(self):
        """获取或创建飞书客户端"""
        if not self._client and self.app_id and self.app_secret:
            self._client = Lark(
                app_id=self.app_id,
                app_secret=self.app_secret
            )
        return self._client
    
    async def push(self, news_item: Dict[str, Any]) -> PushResult:
        """推送新闻到飞书"""
        try:
            if self.webhook:
                # 使用Webhook方式
                return await self._push_by_webhook(news_item)
            elif self._get_client() and self.chat_id:
                # 使用API方式
                return await self._push_by_api(news_item)
            else:
                return PushResult(
                    success=False,
                    channel='feishu',
                    error_message='未配置飞书推送参数'
                )
        except Exception as e:
            return PushResult(
                success=False,
                channel='feishu',
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    async def _push_by_webhook(self, news_item: Dict[str, Any]) -> PushResult:
        """通过Webhook推送"""
        import aiohttp
        import json
        
        score = news_item.get('final_score', 0)
        card = self._build_card(news_item)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook,
                json={"msg_type": "interactive", "card": card},
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('code') == 0:
                        return PushResult(
                            success=True,
                            channel='feishu',
                            message_id=result.get('data', {}).get('message_id'),
                            timestamp=datetime.now().isoformat()
                        )
                    else:
                        return PushResult(
                            success=False,
                            channel='feishu',
                            error_message=result.get('msg', 'Unknown error')
                        )
                else:
                    return PushResult(
                        success=False,
                        channel='feishu',
                        error_message=f'HTTP {response.status}'
                    )
    
    async def _push_by_api(self, news_item: Dict[str, Any]) -> PushResult:
        """通过API推送（需要更完整的飞书SDK实现）"""
        # 这里简化处理，实际应使用飞书SDK
        return PushResult(
            success=False,
            channel='feishu',
            error_message='API模式暂未完全实现，请使用Webhook'
        )
    
    def _build_card(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """构建飞书消息卡片"""
        score = news_item.get('final_score', 0)
        title = news_item.get('title', '无标题')
        summary = news_item.get('summary', '')[:300]
        source = news_item.get('source', '未知来源')
        url = news_item.get('url', '')
        
        # 根据分数设置颜色
        if score >= 85:
            header_color = 'red'
            tag_text = '🔥 重要'
        elif score >= 70:
            header_color = 'orange'
            tag_text = '⚡ 关注'
        else:
            header_color = 'blue'
            tag_text = '💡 一般'
        
        return {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📊 {score}% | {title[:50]}..."
                },
                "template": header_color
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**{tag_text}**\n{summary}..."
                    }
                },
                {
                    "tag": "div",
                    "fields": [
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**📎 来源:** {source}"}},
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**🏷️ 分类:** {', '.join(news_item.get('categories', [])[:3])}"}}
                    ]
                },
                {"tag": "hr"},
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {"tag": "plain_text", "content": "🔗 阅读原文"},
                            "type": "primary",
                            "url": url
                        }
                    ]
                }
            ]
        }
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            if self.webhook:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.webhook,
                        json={"msg_type": "text", "content": {"text": "测试消息"}}
                    ) as response:
                        return response.status == 200
            return False
        except:
            return False
