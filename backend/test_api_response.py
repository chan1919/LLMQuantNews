#!/usr/bin/env python3
"""
测试API接口是否正确返回AI分析数据
"""
import requests
import json

def test_api():
    """测试API接口"""
    url = "http://localhost:8000/api/v1/news/feed"
    params = {"offset": 0, "limit": 2}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        print("=== API接口测试结果 ===")
        print(f"状态码: {response.status_code}")
        print(f"总数量: {data.get('total', 0)}")
        print(f"返回条数: {len(data.get('items', []))}")
        
        if data.get('items'):
            print("\n=== 第一条新闻数据 ===")
            first_item = data['items'][0]
            
            # 检查AI分析字段
            ai_fields = [
                'ai_score', 'market_impact', 'industry_relevance', 
                'novelty_score', 'urgency', 'sentiment', 'is_analyzed'
            ]
            
            print("\nAI分析字段检查:")
            for field in ai_fields:
                value = first_item.get(field)
                if value is not None:
                    print(f"  ✓ {field}: {value}")
                else:
                    print(f"  ✗ {field}: 缺失")
            
            print("\n完整数据示例:")
            print(json.dumps(first_item, indent=2, ensure_ascii=False))
        else:
            print("没有返回任何新闻数据")
            
    except Exception as e:
        print(f"API请求失败: {e}")

if __name__ == "__main__":
    test_api()
