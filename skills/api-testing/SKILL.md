---
name: api-testing
description: 测试后端 API 端点的完整性和正确性，包括 REST 接口、WebSocket、错误处理等
---

## 测试范围

### 1. REST API 测试
- **新闻相关端点**:
  - `GET /api/v1/news` - 获取新闻列表
  - `GET /api/v1/news/{id}` - 获取新闻详情
  - `POST /api/v1/news` - 创建新闻 (管理用)
  - `DELETE /api/v1/news/{id}` - 删除新闻

- **配置相关端点**:
  - `GET /api/v1/config/sources` - 获取信息源配置
  - `POST /api/v1/config/sources` - 添加信息源
  - `PUT /api/v1/config/sources/{id}` - 更新信息源
  - `DELETE /api/v1/config/sources/{id}` - 删除信息源

- **仪表盘端点**:
  - `GET /api/v1/dashboard/stats` - 统计数据
  - `GET /api/v1/dashboard/charts` - 图表数据

- **成本端点**:
  - `GET /api/v1/costs/stats` - 成本统计
  - `GET /api/v1/costs/breakdown` - 成本明细

### 2. 测试类型
- **连通性测试**: 端点可访问 (HTTP 200/201/204)
- **参数验证**: 必填参数、类型检查、边界值
- **响应验证**: 数据结构、字段类型、数据准确性
- **错误处理**: 400/401/403/404/500 错误响应
- **性能测试**: 响应时间、并发能力
- **认证测试**: JWT/API Key 认证 (如启用)

## 测试流程

```
1. 启动服务
   └── 确保 FastAPI 服务运行 (测试环境)

2. 基础测试
   ├── 健康检查 /health
   ├── API 文档 /docs (Swagger)
   └── 版本检查 /api/v1/version

3. 端点测试
   ├── 正向测试 (有效参数)
   ├── 反向测试 (无效参数)
   ├── 边界测试 (极限值)
   └── 异常测试 (网络/数据库故障)

4. 集成测试
   ├── API + 数据库
   ├── API + Celery 任务
   └── API + 外部服务

5. 生成报告
   ├── 端点覆盖率
   ├── 测试通过率
   ├── 响应时间统计
   └── 问题清单
```

## 测试实现

### 测试脚本位置
```
backend/tests/test_api.py
backend/tests/integration/
backend/tests/test_websocket.py
```

### 测试工具
- **pytest**: 测试框架
- **httpx**: 异步 HTTP 客户端
- **TestClient**: FastAPI 测试客户端
- **pytest-asyncio**: 异步测试支持

### 核心测试方法

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 新闻列表 API 测试
def test_get_news_list():
    """测试获取新闻列表"""
    
    # 正向测试
    response = client.get("/api/v1/news")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    
    # 验证分页参数
    response = client.get("/api/v1/news?page=1&limit=20")
    assert response.status_code == 200
    assert len(data["items"]) <= 20
    
    # 验证过滤参数
    response = client.get("/api/v1/news?source=hackernews&min_score=80")
    assert response.status_code == 200
    
    # 验证排序参数
    response = client.get("/api/v1/news?sort_by=score&order=desc")
    assert response.status_code == 200

# 新闻详情 API 测试
def test_get_news_detail():
    """测试获取新闻详情"""
    
    # 存在的数据
    response = client.get("/api/v1/news/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "content" in data
    
    # 不存在的数据
    response = client.get("/api/v1/news/999999")
    assert response.status_code == 404
    assert "detail" in response.json()

# 信息源配置 API 测试
def test_source_crud():
    """测试信息源 CRUD 操作"""
    
    # 创建
    new_source = {
        "name": "Test RSS",
        "crawler_type": "rss",
        "source_url": "https://example.com/rss",
        "interval_seconds": 3600,
        "priority": 5
    }
    response = client.post("/api/v1/config/sources", json=new_source)
    assert response.status_code == 201
    source_id = response.json()["id"]
    
    # 读取
    response = client.get(f"/api/v1/config/sources/{source_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test RSS"
    
    # 更新
    update_data = {"priority": 10}
    response = client.put(
        f"/api/v1/config/sources/{source_id}",
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["priority"] == 10
    
    # 删除
    response = client.delete(f"/api/v1/config/sources/{source_id}")
    assert response.status_code == 204
    
    # 验证删除
    response = client.get(f"/api/v1/config/sources/{source_id}")
    assert response.status_code == 404

# 错误处理测试
def test_error_handling():
    """测试错误处理"""
    
    # 无效参数
    response = client.get("/api/v1/news?page=-1")
    assert response.status_code == 422  # Validation Error
    
    # 类型错误
    response = client.get("/api/v1/news?limit=abc")
    assert response.status_code == 422
    
    # 未授权 (如启用认证)
    # response = client.get("/api/v1/admin/stats")
    # assert response.status_code == 401
    
    # 数据库错误 (模拟)
    # 使用 mock 让数据库抛出异常
    # response = client.get("/api/v1/news")
    # assert response.status_code == 500
```

### 性能测试

```python
import time
from concurrent.futures import ThreadPoolExecutor

def test_api_performance():
    """API 性能测试"""
    
    # 单次响应时间
    start = time.time()
    response = client.get("/api/v1/news")
    elapsed = time.time() - start
    
    assert elapsed < 2.0  # 要求 2 秒内响应
    assert response.status_code == 200
    
    # 并发测试
    def make_request():
        return client.get("/api/v1/news")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: make_request(), range(100)))
    
    success_count = sum(1 for r in results if r.status_code == 200)
    assert success_count >= 95  # 95% 成功率

# 压力测试
def test_stress():
    """压力测试"""
    import asyncio
    import httpx
    
    async def stress_test():
        async with httpx.AsyncClient() as client:
            tasks = []
            for _ in range(1000):
                task = client.get("http://localhost:8000/api/v1/news")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            return responses
    
    responses = asyncio.run(stress_test())
    success = sum(1 for r in responses if r.status_code == 200)
    assert success >= 950  # 95% 成功率
```

## 报告格式

### 控制台输出
```
========================================
API 端点测试报告
========================================

基础端点 (3 个):
✓ GET /health              [PASS]  12ms
✓ GET /docs                [PASS]  45ms
✓ GET /api/v1/version      [PASS]  8ms

新闻 API (5 个):
✓ GET /api/v1/news         [PASS]  156ms  返回 25 条
✓ GET /api/v1/news/{id}    [PASS]  45ms   数据完整
✗ POST /api/v1/news        [FAIL]  403    需要认证
✓ DELETE /api/v1/news/{id} [PASS]  89ms

配置 API (4 个):
✓ GET /api/v1/config/sources   [PASS]  67ms
✓ POST /api/v1/config/sources  [PASS]  123ms
✓ PUT /api/v1/config/sources   [PASS]  98ms
✓ DELETE /api/v1/config/sources [PASS]  76ms

错误处理:
✓ 无效参数返回 422      [PASS]
✓ 不存在资源返回 404    [PASS]
✓ 服务器错误返回 500    [PASS]

性能测试:
✓ 平均响应时间 < 200ms  [PASS]  145ms
✓ 并发成功率 > 95%      [PASS]  98%

========================================
总计：16 个端点
通过：15 个 | 失败：1 个
覆盖率：94%
========================================
```

### JSON 报告
```json
{
  "summary": {
    "total_endpoints": 16,
    "pass": 15,
    "fail": 1,
    "coverage": "94%",
    "avg_response_time": 145,
    "p95_response_time": 234,
    "p99_response_time": 456
  },
  "endpoints": [
    {
      "method": "GET",
      "path": "/api/v1/news",
      "status": "pass",
      "response_time": 156,
      "tests_passed": 5,
      "tests_failed": 0
    }
  ],
  "issues": [
    {
      "endpoint": "POST /api/v1/news",
      "issue": "需要认证但未文档化",
      "severity": "medium",
      "suggestion": "在 API 文档中标明认证要求"
    }
  ]
}
```

## 运行测试

```bash
# 所有 API 测试
python -m pytest backend/tests/test_api.py -v

# 特定端点测试
python -m pytest backend/tests/test_api.py::test_get_news_list -v

# 集成测试
python -m pytest backend/tests/integration/ -v

# 性能测试
python -m pytest backend/tests/test_performance.py -v

# 生成覆盖率报告
python -m pytest backend/tests/ --cov=app --cov-report=html

# 生成 HTML 报告
python -m pytest backend/tests/test_api.py --html=reports/api_report.html
```

## 常见问题

### 1. 数据库连接失败
- 检查测试数据库配置
- 确保数据库服务运行
- 验证连接字符串

### 2. 认证失败
- 检查 JWT/API Key 配置
- 在测试中添加认证头
- 确认测试环境是否启用认证

### 3. 响应时间过长
- 检查数据库查询性能
- 添加索引优化
- 使用缓存

### 4. 测试数据污染
- 使用事务回滚
- 每个测试使用独立数据
- 测试后清理数据

## CI/CD 集成

```yaml
# .github/workflows/api-tests.yml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      
      - name: Run API tests
        run: |
          cd backend
          pytest tests/test_api.py --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 最佳实践

1. **测试隔离**: 每个测试使用独立数据，互不影响
2. **事务回滚**: 使用 pytest fixtures 自动回滚数据库变更
3. **Mock 外部服务**: 避免测试依赖外部 API
4. **参数化测试**: 使用 @pytest.mark.parametrize 减少重复代码
5. **断言明确**: 每个断言只验证一件事
6. **测试命名**: 使用描述性名称说明测试目的
