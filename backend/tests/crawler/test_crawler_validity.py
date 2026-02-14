#!/usr/bin/env python3
"""
测试信息源有效性的模块
"""

import requests
import feedparser
import time
from datetime import datetime
from typing import Dict, Tuple, Optional

class CrawlerValidityTester:
    """
    信息源有效性测试器
    """
    
    def __init__(self, timeout: int = 10):
        """
        初始化测试器
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
    
    def test_crawler(self, crawler_config: Dict) -> Tuple[bool, str]:
        """
        测试信息源的有效性
        
        Args:
            crawler_config: 爬虫配置字典
            
        Returns:
            Tuple[bool, str]: (是否有效, 测试结果消息)
        """
        crawler_type = crawler_config.get('crawler_type')
        source_url = crawler_config.get('source_url')
        
        if not source_url:
            return False, "缺少source_url配置"
        
        # 首先测试URL可访问性
        try:
            response = requests.get(source_url, timeout=self.timeout)
            if response.status_code != 200:
                return False, f"URL访问失败，状态码: {response.status_code}"
        except requests.RequestException as e:
            return False, f"URL访问错误: {str(e)}"
        
        # 根据爬虫类型进行特定测试
        if crawler_type == 'rss':
            return self._test_rss_source(source_url)
        elif crawler_type == 'web':
            return self._test_web_source(source_url)
        elif crawler_type == 'api':
            return self._test_api_source(source_url)
        elif crawler_type == 'custom':
            return self._test_custom_crawler(crawler_config)
        else:
            return True, "未知爬虫类型，仅验证了URL可访问性"
    
    def _test_rss_source(self, url: str) -> Tuple[bool, str]:
        """
        测试RSS源的有效性
        
        Args:
            url: RSS源URL
            
        Returns:
            Tuple[bool, str]: (是否有效, 测试结果消息)
        """
        try:
            feed = feedparser.parse(url)
            
            # 检查是否有解析错误
            if feed.get('bozo'):
                error = feed.get('bozo_exception')
                return False, f"RSS解析错误: {str(error)}"
            
            # 检查是否有条目
            if not feed.get('entries'):
                return False, "RSS源无内容"
            
            # 检查必要字段
            sample_entry = feed['entries'][0]
            required_fields = ['title', 'link']
            missing_fields = [field for field in required_fields if field not in sample_entry]
            
            if missing_fields:
                return False, f"RSS条目缺少必要字段: {', '.join(missing_fields)}"
            
            return True, f"RSS源有效，包含 {len(feed['entries'])} 条内容"
        except Exception as e:
            return False, f"RSS测试错误: {str(e)}"
    
    def _test_web_source(self, url: str) -> Tuple[bool, str]:
        """
        测试网页源的有效性
        
        Args:
            url: 网页URL
            
        Returns:
            Tuple[bool, str]: (是否有效, 测试结果消息)
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            
            # 检查页面内容是否为空
            if not response.text or len(response.text.strip()) < 100:
                return False, "网页内容为空或过短"
            
            # 检查是否为HTML页面
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                return False, "URL返回的不是HTML内容"
            
            return True, "网页源可访问"
        except Exception as e:
            return False, f"网页测试错误: {str(e)}"
    
    def _test_api_source(self, url: str) -> Tuple[bool, str]:
        """
        测试API源的有效性
        
        Args:
            url: API URL
            
        Returns:
            Tuple[bool, str]: (是否有效, 测试结果消息)
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            
            # 检查是否为JSON响应
            try:
                data = response.json()
                return True, "API返回有效JSON数据"
            except ValueError:
                return False, "API返回的不是有效JSON数据"
        except Exception as e:
            return False, f"API测试错误: {str(e)}"
    
    def _test_custom_crawler(self, crawler_config: Dict) -> Tuple[bool, str]:
        """
        测试自定义爬虫的有效性
        
        Args:
            crawler_config: 爬虫配置字典
            
        Returns:
            Tuple[bool, str]: (是否有效, 测试结果消息)
        """
        try:
            # 检查是否有自定义脚本
            custom_script = crawler_config.get('custom_script')
            if not custom_script:
                return False, "自定义爬虫缺少脚本"
            
            # 检查脚本是否为有效字符串
            if not isinstance(custom_script, str) or len(custom_script.strip()) < 10:
                return False, "自定义脚本内容过短或无效"
            
            return True, "自定义爬虫配置完整"
        except Exception as e:
            return False, f"自定义爬虫测试错误: {str(e)}"

# 示例用法
if __name__ == "__main__":
    tester = CrawlerValidityTester()
    
    # 测试有效的RSS源
    test_config1 = {
        "name": "新浪新闻-国内",
        "crawler_type": "rss",
        "source_url": "http://rss.sina.com.cn/news/marquee/ddt.xml"
    }
    
    # 测试无效的URL
    test_config2 = {
        "name": "无效测试源",
        "crawler_type": "rss",
        "source_url": "http://example.com/nonexistent"
    }
    
    print("测试1 - 新浪新闻RSS:")
    is_valid, message = tester.test_crawler(test_config1)
    print(f"结果: {'有效' if is_valid else '无效'}")
    print(f"消息: {message}")
    print()
    
    print("测试2 - 无效URL:")
    is_valid, message = tester.test_crawler(test_config2)
    print(f"结果: {'有效' if is_valid else '无效'}")
    print(f"消息: {message}")
