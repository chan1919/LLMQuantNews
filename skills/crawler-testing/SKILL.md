---
name: crawler-testing
description: 测试所有爬虫和信息源是否正常运行，支持RSS、Web、API、Custom四种类型，生成连通性测试报告
---

## 测试范围

### 1. RSS爬虫测试
- **RSSCrawler**: 标准RSS feed（XML格式）
- **AtomCrawler**: Atom feed格式
- **测试项**: 
  - URL可访问性（HTTP 200）
  - XML解析有效性
  - 内容提取正常（title、link、pubDate）

### 2. Web爬虫测试
- **WebCrawler**: 普通网页爬取
- **SinglePageCrawler**: 单页内容提取
- **测试项**:
  - 目标URL可访问
  - 页面内容可解析
  - CSS选择器/正则规则有效
  - 反爬措施检测（403/验证码等）

### 3. API爬虫测试
- **APICrawler**: 通用API接口
- **NewsAPICrawler**: 新闻专用API（如NewsAPI）
- **测试项**:
  - API端点连通性
  - 认证有效性（API Key等）
  - 响应格式正确（JSON）
  - 速率限制检查

### 4. Custom爬虫测试
- **CustomCrawler**: 自定义脚本
- **测试项**:
  - 脚本语法正确性
  - 依赖导入正常
  - fetch()方法可执行
  - parse()方法返回有效数据

## 测试流程

```
1. 加载配置
   └── 读取所有配置的爬虫信息

2. 分类测试
   ├── RSS测试组
   ├── Web测试组
   ├── API测试组
   └── Custom测试组

3. 执行测试
   ├── 连通性测试（网络层）
   ├── 数据解析测试（应用层）
   └── 异常处理测试

4. 生成报告
   ├── 成功率统计
   ├── 响应时间统计
   ├── 错误详情
   └── 修复建议
```

## 测试实现

### 测试脚本位置
```
backend/tests/test_crawlers.py
backend/tests/test_sources.py
```

### 核心测试方法

```python
# RSS测试示例
async def test_rss_crawler(config: dict) -> TestResult:
    crawler = RSSCrawler(config)
    
    # 测试1: 连通性
    try:
        raw_data = await crawler.fetch()
        connectivity = TestStatus.PASS
    except Exception as e:
        connectivity = TestStatus.FAIL
        error_msg = str(e)
    
    # 测试2: 数据解析
    try:
        items = await crawler.crawl()
        parsing = TestStatus.PASS if items else TestStatus.WARN
    except Exception as e:
        parsing = TestStatus.FAIL
    
    return TestResult(
        name=config['name'],
        type='rss',
        connectivity=connectivity,
        parsing=parsing,
        response_time=elapsed,
        error=error_msg
    )
```

### 批量测试

```python
async def test_all_crawlers():
    """测试所有配置的信息源"""
    configs = load_crawler_configs()
    
    results = []
    for config in configs:
        crawler_type = config.get('crawler_type')
        
        if crawler_type == 'rss':
            result = await test_rss_crawler(config)
        elif crawler_type == 'web':
            result = await test_web_crawler(config)
        elif crawler_type == 'api':
            result = await test_api_crawler(config)
        elif crawler_type == 'custom':
            result = await test_custom_crawler(config)
        
        results.append(result)
    
    return generate_report(results)
```

## 报告格式

### 控制台输出
```
========================================
爬虫连通性测试报告
========================================

RSS 信息源 (3个):
✓ Hacker News RSS     [PASS]  234ms  25条数据
✓ TechCrunch RSS      [PASS]  567ms  10条数据
✗ Example RSS         [FAIL]  超时   连接失败: Connection timeout

Web 信息源 (2个):
✓ Arxiv Papers        [PASS]  890ms  15条数据
⚠ GitHub Trending     [WARN]  1200ms 0条数据 (可能反爬)

API 信息源 (2个):
✓ NewsAPI             [PASS]  345ms  20条数据
✗ Custom API          [FAIL]  403    认证失败: Invalid API key

Custom 脚本 (1个):
✓ GitHub Stars        [PASS]  456ms  8条数据

========================================
总计: 8个信息源
通过: 5个 | 警告: 1个 | 失败: 2个
========================================
```

### JSON报告
```json
{
  "summary": {
    "total": 8,
    "pass": 5,
    "warn": 1,
    "fail": 2,
    "success_rate": "62.5%"
  },
  "results": [
    {
      "name": "Hacker News RSS",
      "type": "rss",
      "status": "pass",
      "response_time": 234,
      "items_count": 25,
      "tested_at": "2025-02-14T10:30:00Z"
    }
  ]
}
```

## 运行测试

```bash
# 测试单个信息源
python -m pytest tests/test_crawlers.py::test_hacker_news -v

# 测试所有信息源
python -m pytest tests/test_crawlers.py -v

# 生成HTML报告
python -m pytest tests/test_crawlers.py --html=report.html

# 异步测试
python backend/tests/test_sources.py
```

## 修复建议

### 常见问题

1. **连接超时**
   - 增加timeout设置
   - 检查网络/代理配置
   - 确认源地址是否变更

2. **403 Forbidden**
   - 检查User-Agent设置
   - 添加请求头（Referer等）
   - 考虑使用代理

3. **数据解析失败**
   - 检查CSS选择器/XPath
   - 确认页面结构是否变更
   - 更新解析规则

4. **API认证失败**
   - 验证API Key有效性
   - 检查Key是否过期
   - 确认请求参数格式

## 定时监控

建议设置定时任务定期测试：

```bash
# crontab -e
# 每2小时测试一次信息源
0 */2 * * * cd /path/to/backend && python -m pytest tests/test_crawlers.py -q
```
