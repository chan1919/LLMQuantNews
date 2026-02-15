import requests
import json

# 调用AI分析API
url = "http://localhost:8000/api/v1/ai/analyze-unanalyzed"
params = {"limit": 10}

try:
    response = requests.post(url, params=params, timeout=120)
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"错误: {e}")
