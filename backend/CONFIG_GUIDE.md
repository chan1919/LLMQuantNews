# LLMQuant News 配置管理指南

## 当前配置状态

### 信息源配置
- ✅ 已配置 9 个高质量信息源
- ✅ 7 个国内源 + 2 个国际源
- ✅ 所有源已验证可用

### 用户配置
- ✅ 默认用户配置已创建
- ✅ 包含 19 个关键词配置
- ✅ 5 个关注行业
- ✅ 5 个关注分类
- ✅ 推送阈值：60 分

---

## 配置说明

### 1. 推送阈值配置

**位置**: `UserConfig.min_score_threshold`

**当前值**: 60 分

**推荐配置**:
- 保守型：70-80 分（只推送最重要的新闻）
- 平衡型：60-70 分（默认）
- 激进型：50-60 分（推送更多新闻）

**修改方法**:
```python
from app.database import SessionLocal
from app.models import UserConfig

db = SessionLocal()
config = db.query(UserConfig).filter(UserConfig.user_id == "default").first()
config.min_score_threshold = 70  # 调整为 70 分
db.commit()
```

---

### 2. 多空敏感度

**位置**: `UserConfig.position_sensitivity`

**当前值**: 1.0（正常）

**推荐配置**:
- 低敏感：0.5-0.8（减少多空波动）
- 正常：1.0（默认）
- 高敏感：1.5-2.0（放大多空判断）

**影响**:
- 敏感度越高，多空判断越明显
- 敏感度高时，利多/利空幅度会放大

---

### 3. 关键词权重

**位置**: `UserConfig.keywords`

**当前配置**: 19 个关键词

**权重说明**:
- 1.0-1.5: 一般关注
- 1.5-2.0: 重点关注
- 2.0-3.0: 高度关注

**添加关键词**:
```python
config.keywords["新能源汽车"] = 2.0
config.keywords["量子计算"] = 1.8
```

---

### 4. 关键词多空配置

**位置**: `UserConfig.keyword_positions`

**当前配置**: 5 个关键词

**格式**:
```python
{
    "关键词": {
        "bias": "bullish",  # bullish/bearish/neutral
        "magnitude": 75     # 0-100%
    }
}
```

**示例**:
- "降息": {"bias": "bullish", "magnitude": 75}
- "加息": {"bias": "bearish", "magnitude": 75}

---

### 5. 影响维度权重

**位置**: `UserConfig.dimension_weights`

**当前配置**:
- 市场影响：30%
- 行业影响：25%
- 政策影响：25%
- 技术影响：20%

**调整方法**:
```python
config.dimension_weights = {
    "market": 0.35,    # 提高市场影响权重
    "industry": 0.25,
    "policy": 0.25,
    "tech": 0.15,
}
```

---

### 6. 来源偏好

**位置**: `UserConfig.preferred_sources`

**当前配置**: 4 个偏好来源

**权重说明**:
- 1.0: 正常权重
- 1.2: 轻度偏好
- 1.5: 中度偏好
- 2.0: 强烈偏好

**添加来源**:
```python
config.preferred_sources["Reuters"] = 1.5
config.preferred_sources["Bloomberg"] = 1.5
```

---

## 评分系统说明

### 最终评分计算
```
final_score = AI 评分 × 0.6 + 规则评分 × 0.4
```

### AI 评分维度
1. 市场影响 (30%)
2. 行业相关性 (25%)
3. 新颖性 (25%)
4. 紧急性 (20%)

### 规则评分因子
- 关键词匹配：标题×2，内容×1
- 行业匹配：+15 分/个
- 来源权重：Reuters/Bloomberg +20 分
- 时效性：1 小时内 +10 分
- 排除关键词：-30 分

---

## 推送优先级

| 分数范围 | 优先级 | 推送策略 |
|---------|--------|---------|
| ≥85 分 | High | 立即推送 |
| 70-84 分 | Medium | 批量推送 |
| 60-69 分 | Low | 达到阈值推送 |
| <60 分 | - | 不推送 |

---

## 常用配置场景

### 场景 1: 只关注重大新闻
```python
config.min_score_threshold = 75
config.ai_weight = 0.7
config.position_sensitivity = 0.8
```

### 场景 2: 关注科技行业
```python
config.keywords["AI"] = 3.0
config.keywords["芯片"] = 2.5
config.keywords["大模型"] = 2.5
config.industries = ["科技", "人工智能", "半导体"]
```

### 场景 3: 高敏感多空分析
```python
config.position_sensitivity = 1.5
config.keyword_positions["财报"] = {
    "bias": "bullish",
    "magnitude": 80
}
```

---

## 配置管理脚本

### 查看当前配置
```bash
cd backend
python -c "from app.database import SessionLocal; from app.models import UserConfig; db=SessionLocal(); c=db.query(UserConfig).first(); print(c.to_dict()); db.close()"
```

### 重置配置
```bash
python scripts/setup_default_config.py
```

---

## 监控与维护

### 检查推送效果
- 查看推送日志：`app/push/`
- 检查推送成功率
- 调整推送阈值

### 优化关键词
- 定期检查关键词匹配情况
- 根据实际效果调整权重
- 添加新的关注关键词

### 更新信息源
- 定期运行 `python test_all_sources.py`
- 停用失效源
- 添加新的优质源

---

## 技术支持

如需进一步定制配置，请参考：
- 评分引擎：`app/scoring/engine.py`
- 筛选服务：`app/services/news_filter.py`
- LLM 引擎：`app/llm/engine.py`
