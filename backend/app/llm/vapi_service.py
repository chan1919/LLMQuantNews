import aiohttp
import json
from typing import List, Dict, Any
from app.config import settings

class VAPIService:
    """V-API服务类 - 用于获取模型列表和管理V-API配置"""
    
    def __init__(self):
        self.api_base = settings.VAPI_BASE_URL or "https://api.vveai.com"
        self.api_key = settings.VAPI_API_KEY or "sk-CERAboOBa75A0dWiB923721a3132469dAaDb44Ee38E52e09"
        self.models_cache = None
        self.cache_expiry = 3600  # 缓存过期时间（秒）
    
    async def get_models(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """
        获取V-API支持的模型列表
        
        Args:
            refresh: 是否刷新缓存
            
        Returns:
            模型列表，每个模型包含id、object、created、owned_by等字段
        """
        if not refresh and self.models_cache:
            return self.models_cache
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/v1/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.models_cache = data.get("data", [])
                        return self.models_cache
                    else:
                        return []
        except Exception as e:
            print(f"获取V-API模型列表失败: {e}")
            return []
    
    async def get_chat_models(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """
        获取V-API支持的聊天模型列表
        
        Args:
            refresh: 是否刷新缓存
            
        Returns:
            聊天模型列表
        """
        all_models = await self.get_models(refresh)
        # 过滤出聊天相关的模型
        chat_models = []
        for model in all_models:
            model_id = model.get("id", "")
            # 排除明显不是聊天模型的类型
            if any(exclude in model_id.lower() for exclude in ["embedding", "whisper", "tts", "dall-e", "image", "vision", "text-", "code-", "music", "video"]):
                continue
            chat_models.append(model)
        return chat_models

# 全局V-API服务实例
vapi_service = VAPIService()