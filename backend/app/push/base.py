from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PushResult:
    """推送结果"""
    success: bool
    channel: str
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: Optional[str] = None

class BasePusher(ABC):
    """推送基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def push(self, news_item: Dict[str, Any]) -> PushResult:
        """推送单条新闻"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """测试连接"""
        pass
    
    def format_message(self, news_item: Dict[str, Any]) -> str:
        """格式化消息内容"""
        score = news_item.get('final_score', 0)
        title = news_item.get('title', '无标题')
        summary = news_item.get('summary', '')[:200]
        source = news_item.get('source', '未知来源')
        url = news_item.get('url', '')
        
        return f"""
📊 重要度: {score}%
📰 {title}

{summary}...

📎 来源: {source}
🔗 {url}
""".strip()
    
    def get_priority_color(self, score: float) -> str:
        """根据分数获取优先级颜色"""
        if score >= 85:
            return 'red'  # 高优先级
        elif score >= 70:
            return 'orange'  # 中优先级
        else:
            return 'blue'  # 低优先级
