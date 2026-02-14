import os
import sys
import importlib.util
import asyncio
from typing import List, Dict, Any, Type, Optional
from pathlib import Path

from .base import BaseNewsCrawler, NewsItem

class CustomCrawler(BaseNewsCrawler):
    """自定义爬虫 - 加载用户上传的Python脚本"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.script_content = config.get('custom_script', '')
        self.script_path = config.get('custom_config', {}).get('script_path')
        self._crawler_instance = None
    
    @classmethod
    def get_type(cls) -> str:
        return "custom"
    
    def _load_script(self) -> Optional[Type[BaseNewsCrawler]]:
        """动态加载用户脚本"""
        try:
            # 创建临时模块
            spec = importlib.util.spec_from_loader("custom_crawler", loader=None)
            module = importlib.util.module_from_spec(spec)
            
            # 执行脚本内容
            if self.script_content:
                exec(self.script_content, module.__dict__)
            elif self.script_path and os.path.exists(self.script_path):
                with open(self.script_path, 'r', encoding='utf-8') as f:
                    exec(f.read(), module.__dict__)
            else:
                return None
            
            # 查找爬虫类
            for name, obj in module.__dict__.items():
                if (isinstance(obj, type) and 
                    issubclass(obj, BaseNewsCrawler) and 
                    obj != BaseNewsCrawler and
                    obj != CustomCrawler):
                    return obj
            
            return None
        except Exception as e:
            print(f"加载自定义脚本失败: {e}")
            return None
    
    async def fetch(self) -> List[Dict[str, Any]]:
        """调用自定义爬虫的fetch方法"""
        crawler_class = self._load_script()
        if not crawler_class:
            return []
        
        try:
            self._crawler_instance = crawler_class(self.config)
            return await self._crawler_instance.fetch()
        except Exception as e:
            print(f"自定义爬虫fetch失败: {e}")
            return []
    
    async def parse(self, raw_data: Dict[str, Any]) -> Optional[NewsItem]:
        """调用自定义爬虫的parse方法"""
        if self._crawler_instance:
            return await self._crawler_instance.parse(raw_data)
        return None

class CustomScriptManager:
    """自定义脚本管理器"""
    
    SCRIPTS_DIR = Path("crawler_scripts")
    
    @classmethod
    def list_scripts(cls) -> List[Dict[str, Any]]:
        """列出所有自定义脚本"""
        scripts = []
        if cls.SCRIPTS_DIR.exists():
            for script_file in cls.SCRIPTS_DIR.glob("*.py"):
                scripts.append({
                    'name': script_file.stem,
                    'path': str(script_file),
                    'size': script_file.stat().st_size,
                })
        return scripts
    
    @classmethod
    def save_script(cls, name: str, content: str) -> str:
        """保存自定义脚本"""
        cls.SCRIPTS_DIR.mkdir(exist_ok=True)
        script_path = cls.SCRIPTS_DIR / f"{name}.py"
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(script_path)
    
    @classmethod
    def delete_script(cls, name: str) -> bool:
        """删除自定义脚本"""
        script_path = cls.SCRIPTS_DIR / f"{name}.py"
        if script_path.exists():
            script_path.unlink()
            return True
        return False
    
    @classmethod
    def load_script_content(cls, name: str) -> Optional[str]:
        """加载脚本内容"""
        script_path = cls.SCRIPTS_DIR / f"{name}.py"
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
