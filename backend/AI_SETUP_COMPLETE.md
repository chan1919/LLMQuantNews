# LLMQuant News - AI 配置完成报告

## 配置状态

### V-API 配置 [OK]
- **Base URL**: https://api.vveai.com/v1
- **API Key**: sk-CERA...52e09 (已配置)
- **可用模型**: 407 个
- **测试状态**: 成功

### 默认模型
- **模型**: deepseek-chat (通过 V-API)
- **Provider**: OpenAI-compatible
- **状态**: 已验证可用

---

## 已配置的 AI 功能

### 1. 新闻摘要生成
- 自动生成 100 字以内的简明摘要
- 使用 gpt-4o-mini 模型
- Token 消耗：~100-200 tokens

### 2. 自动分类标记
- 9 个预定义类别
- Finance, Technology, AI, Blockchain, Policy, Market, Company, International, Society
- 支持多标签分类

### 3. 多维 AI 评分
- 市场影响 (30%)
- 行业相关性 (25%)
- 新颖性 (25%)
- 紧急性 (20%)

### 4. 关键词提取
- 自动提取 5-10 个关键词
- 覆盖主题、实体、情感

### 5. 情感分析
- positive / negative / neutral
- 用于多空判断

### 6. 多空分析
- 方向判断：bullish / bearish / neutral
- 幅度计算：0-100%
- 时间维度：短期/中期/长期

### 7. 影响分析
- 市场影响评分
- 行业影响评分
- 政策影响评分
- 技术影响评分

### 8. 成本追踪
- 记录每次 API 调用
- 统计 token 消耗
- 计算 USD/CNY 成本
- 月度预算：$100 USD

---

## 评分系统配置

### 综合评分公式
```
final_score = AI 评分 × 0.6 + 规则评分 × 0.4
```

### 推送阈值
- **High Priority**: ≥85 分 (立即推送)
- **Medium Priority**: 70-84 分 (批量推送)
- **Low Priority**: 60-69 分 (达到阈值推送)
- **No Push**: <60 分 (不推送)

---

## 使用示例

### Python 代码示例
```python
from app.llm.engine import llm_engine

# 快速新闻分析
result = await llm_engine.brief_analyze_with_vapi(
    title="央行宣布降息 25 个基点",
    content="中国人民银行今日宣布...",
    model="deepseek-chat"
)

# 结果包含:
# - summary: 摘要
# - keywords: 关键词列表
# - sentiment: 情感分析
# - categories: 分类
# - importance: 重要性评分
# - position_bias: 多空判断
# - position_magnitude: 多空幅度
# - market_impact: 市场影响
# - industry_relevance: 行业相关性
# - novelty_score: 新颖性
# - urgency: 紧急性
```

### 完整分析任务
```python
result = await llm_engine.process_news(
    title="新闻标题",
    content="新闻内容",
    tasks=['summarize', 'classify', 'score', 'keywords', 'sentiment'],
    model="deepseek-chat"
)
```

---

## 测试命令

### 测试 V-API 连接
```bash
cd backend
python test_simple_ai.py
```

### 测试完整 AI 功能
```bash
python test_ai_config.py
```

### 测试信息源
```bash
python test_all_sources.py
```

---

## 配置文件

### 环境变量 (.env)
```bash
# V-API Configuration
VAPI_BASE_URL=https://api.vveai.com
VAPI_API_KEY=sk-CERAboOBa75A0dWiB923721a3132469dAaDb44Ee38E52e09

# Default Model
DEFAULT_LLM_MODEL=deepseek-chat

# Cost Tracking
ENABLE_COST_TRACKING=True
MONTHLY_BUDGET_USD=100.0
```

### 用户配置 (UserConfig)
```python
{
    "keywords": {"AI": 2.5, "芯片": 2.2, "央行": 2.5},
    "industries": ["科技", "金融", "人工智能"],
    "categories": ["Finance", "Technology", "AI"],
    "min_score_threshold": 60.0,
    "ai_weight": 0.6,
    "rule_weight": 0.4,
    "position_sensitivity": 1.0,
}
```

---

## 成本估算

### 单次新闻分析成本
- **输入**: ~500 tokens
- **输出**: ~200 tokens
- **总计**: ~700 tokens
- **成本**: ~$0.0001 USD (deepseek-chat)

### 每日成本估算
- 100 条新闻/天：~$0.01 USD
- 1000 条新闻/天：~$0.10 USD
- 10000 条新闻/天：~$1.00 USD

### 月度预算
- 设置：$100 USD
- 可处理：~100 万条新闻

---

## 故障排查

### V-API 连接失败
1. 检查 API Key 是否正确
2. 检查网络连接
3. 验证 Base URL 格式

### 模型调用失败
1. 确认模型名称正确
2. 检查 LiteLLM 配置
3. 查看错误日志

### 成本异常
1. 检查 `llm_costs` 表
2. 查看月度使用统计
3. 调整预算限制

---

## 系统状态

- [x] V-API 配置完成
- [x] 模型连接测试通过
- [x] 用户配置已创建
- [x] 评分系统就绪
- [x] 推送阈值已设置
- [x] 成本追踪启用
- [x] 信息源已验证

**系统已就绪，可以开始使用!**

---

## 相关文档

- 配置指南：`CONFIG_GUIDE.md`
- 信息源文档：`SOURCES_SUMMARY.md`
- 测试脚本：`test_ai_config.py`, `test_simple_ai.py`
