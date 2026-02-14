from typing import Dict, Any, List, Type
from .base import BasePusher, PushResult
from .feishu import FeishuPusher
from .email import EmailPusher

class PushManager:
    """推送管理器"""
    
    PUSHERS = {
        'feishu': FeishuPusher,
        'email': EmailPusher,
    }
    
    def __init__(self):
        self._pusher_instances: Dict[str, BasePusher] = {}
    
    def register_pusher(self, name: str, pusher_class: Type[BasePusher]):
        """注册新的推送方式"""
        self.PUSHERS[name] = pusher_class
    
    def create_pusher(self, channel: str, config: Dict[str, Any]) -> BasePusher:
        """创建推送器实例"""
        if channel not in self.PUSHERS:
            raise ValueError(f"未知的推送渠道: {channel}")
        
        pusher_class = self.PUSHERS[channel]
        pusher = pusher_class(config)
        self._pusher_instances[channel] = pusher
        return pusher
    
    async def push(
        self, 
        news_item: Dict[str, Any], 
        channels: List[str],
        configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, PushResult]:
        """向多个渠道推送"""
        results = {}
        
        for channel in channels:
            try:
                config = configs.get(channel, {})
                pusher = self.create_pusher(channel, config)
                result = await pusher.push(news_item)
                results[channel] = result
            except Exception as e:
                results[channel] = PushResult(
                    success=False,
                    channel=channel,
                    error_message=str(e)
                )
        
        return results
    
    async def test_channel(self, channel: str, config: Dict[str, Any]) -> bool:
        """测试指定渠道"""
        try:
            pusher = self.create_pusher(channel, config)
            return await pusher.test_connection()
        except:
            return False
    
    def get_available_channels(self) -> List[str]:
        """获取所有可用渠道"""
        return list(self.PUSHERS.keys())

# 全局推送管理器实例
push_manager = PushManager()
