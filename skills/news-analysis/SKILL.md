---
name: news-analysis
description: 测试和验证新闻 AI 分析功能，包括评分系统、情感分析、关键词提取等
---

## 测试范围

### 1. AI 评分系统测试
- **ScoringService**: 新闻智能评分服务
- **测试项**:
  - 评分模型加载正常
  - 评分 prompt 构建正确
  - API 调用成功 (LiteLLM)
  - 评分结果解析正确 (0-100 分)
  - 错误处理完善 (超时/鉴权失败/格式错误)

### 2. 情感分析测试
- **测试项**:
  - 多空方向判断 (看涨/看跌/中性)
  - 情感强度评分
  - 关键词提取准确性
  - 支持多模型 (Claude/GPT/DeepSeek/Gemini)

### 3. 规则评分测试
- **RuleBasedScorer**: 基于规则的评分
- **测试项**:
  - 关键词匹配规则
  - 来源权重配置
  - 时效性评分
  - 综合评分计算 (AI 评分 + 规则评分)

### 4. 成本追踪测试
- **测试项**:
  - API 调用成本记录
  - token 使用统计
  - 预算告警触发
  - 成本数据持久化

## 测试流程

```
1. 加载配置
   └── 读取 .env 中的 AI 模型配置和 API Keys

2. 单元测试
   ├── 评分服务初始化
   ├── Prompt 构建测试
   ├── API 调用测试 (mock)
   └── 结果解析测试

3. 集成测试
   ├── 真实 API 调用测试
   ├── 多模型兼容性测试
   ├── 错误场景测试
   └── 性能测试 (并发/超时)

4. 生成报告
   ├── 测试通过率
   ├── 响应时间统计
   ├── 成本统计
   └── 问题建议
```

## 测试实现

### 测试脚本位置
```
backend/tests/test_scoring.py
backend/tests/test_ai_analysis.py
backend/test_ai_config.py
```

### 核心测试方法

```python
# 评分系统测试示例
async def test_scoring_service(news_item: News) -> ScoringResult:
    """测试完整的评分流程"""
    
    # 1. 初始化服务
    scoring_service = ScoringService()
    
    # 2. 测试 AI 评分
    try:
        ai_score = await scoring_service.ai_score(news_item)
        ai_status = TestStatus.PASS
    except Exception as e:
        ai_score = None
        ai_status = TestStatus.FAIL
        error_msg = str(e)
    
    # 3. 测试规则评分
    try:
        rule_score = await scoring_service.rule_score(news_item)
        rule_status = TestStatus.PASS
    except Exception as e:
        rule_score = None
        rule_status = TestStatus.FAIL
    
    # 4. 测试综合评分
    try:
        final_score = await scoring_service.calculate_final_score(
            news_item, ai_score, rule_score
        )
        final_status = TestStatus.PASS
    except Exception as e:
        final_score = None
        final_status = TestStatus.FAIL
    
    return ScoringTestResult(
        news_id=news_item.id,
        ai_score=ai_score,
        ai_status=ai_status,
        rule_score=rule_score,
        rule_status=rule_status,
        final_score=final_score,
        final_status=final_status,
        cost=calculate_cost(),
        response_time=elapsed
    )
```

### 批量测试

```python
async def test_all_scoring_models():
    """测试所有配置的 AI 模型"""
    models = [
        "anthropic/claude-3-sonnet-20240229",
        "openai/gpt-3.5-turbo",
        "deepseek/deepseek-chat",
        "google/gemini-pro"
    ]
    
    results = []
    for model in models:
        result = await test_model_scoring(model)
        results.append(result)
    
    return generate_model_comparison_report(results)
```

## 报告格式

### 控制台输出
```
========================================
新闻 AI 分析测试报告
========================================

AI 评分测试 (4 个模型):
✓ Claude 3 Sonnet    [PASS]  1.2s   分数：85  成本：$0.002
✓ GPT-3.5-Turbo      [PASS]  0.8s   分数：82  成本：$0.001
✓ DeepSeek Chat      [PASS]  1.5s   分数：87  成本：$0.0005
⚠ Gemini Pro         [WARN]  3.2s   超时重试后成功

情感分析测试:
✓ 多空方向判断      [PASS]  准确率 95%
✓ 情感强度评分      [PASS]  相关性 0.89
✓ 关键词提取        [PASS]  Top5 准确率 92%

规则评分测试:
✓ 关键词匹配        [PASS]  规则命中 15/20
✓ 来源权重          [PASS]  权重配置正确
✓ 时效性评分        [PASS]  时间计算准确

========================================
总计成本：$0.0035
平均响应时间：1.67s
========================================
```

### JSON 报告
```json
{
  "summary": {
    "total_tests": 12,
    "pass": 11,
    "warn": 1,
    "fail": 0,
    "success_rate": "91.7%",
    "total_cost": 0.0035,
    "avg_response_time": 1.67
  },
  "model_comparison": [
    {
      "model": "claude-3-sonnet",
      "status": "pass",
      "response_time": 1.2,
      "cost": 0.002,
      "avg_score": 85
    }
  ],
  "issues": [
    {
      "test": "Gemini Pro",
      "issue": "响应超时",
      "suggestion": "增加 timeout 或降低并发"
    }
  ]
}
```

## 运行测试

```bash
# 单元测试
python -m pytest backend/tests/test_scoring.py -v

# 集成测试 (需要 API Keys)
python -m pytest backend/tests/test_ai_analysis.py -v

# 特定模型测试
python backend/test_ai_config.py --model claude-3-sonnet

# 成本分析
python backend/test_ai_config.py --analyze-costs

# 生成 HTML 报告
python -m pytest backend/tests/ --html=reports/scoring_report.html
```

## 常见问题

### 1. API 调用失败
- 检查 .env 中的 API Key 配置
- 验证模型名称是否正确 (LiteLLM 格式)
- 检查网络连接/代理配置

### 2. 评分结果异常
- 检查 prompt 模板是否正确
- 验证新闻内容格式
- 查看 LLM 返回的原始响应

### 3. 成本过高
- 优化 prompt 长度
- 使用更便宜的模型 (如 DeepSeek)
- 添加缓存机制避免重复调用

### 4. 响应超时
- 增加 timeout 配置
- 降低并发请求数
- 使用流式响应

## 性能优化建议

1. **批量处理**: 多条新闻合并请求
2. **缓存机制**: 相同内容不重复分析
3. **模型降级**: 主模型失败自动切换备用
4. **异步处理**: 使用 Celery 后台任务

## 监控告警

建议设置以下监控：
- API 调用失败率 > 5% 告警
- 平均响应时间 > 3s 告警
- 日成本超过预算 80% 告警
- 评分异常 (如全部分数>95) 告警
