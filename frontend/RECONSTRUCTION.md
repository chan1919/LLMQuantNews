# 前端重构说明文档

## 概述

前端已从传统的仪表盘模式重构为信息流优先的模式，更符合金融量化新闻阅读场景。

## 主要变更

### 1. 页面结构重构

#### 首页 - 信息流 (FeedList)
- **路由**: `/`
- **功能**: 展示按时间衰减算法排序的新闻信息流
- **排序方式**: 综合评分 × 时间衰减因子
- **加载方式**: 无限滚动加载
- **信息块展示**:
  - 加粗标题
  - 1-2行简短摘要
  - 时间衰减后评分（带颜色标识）
  - 多空判断 + 幅度百分比
  - 一句话影响描述
  - 来源链接

#### 详情页 - NewsDetail
- **路由**: `/news/:id`
- **功能**: 展示完整新闻信息和多维度影响分析
- **内容包括**:
  - 完整标题和元信息
  - 综合评分 + 多空判断
  - 4维度影响分析卡片（市场/行业/政策/技术）
  - 每个维度含：评分条、多空标识、150字分析
  - 关键词和分类标签
  - 完整内容 + 原文链接

#### 历史记录 - NewsList
- **路由**: `/history`
- **功能**: 原新闻列表页，保留传统表格视图

#### 配置管理 - Config
- **路由**: `/config`
- **新增标签页**:
  - **相关性配置**: 行业、关键词、排除词
  - **多空配置**: 敏感度、维度权重、时间范围、关键词多空设置
  - **基础配置**: 评分权重、AI模型配置
  - **爬虫管理**: 爬虫配置（开发中）
  - **推送配置**: 飞书/邮件推送配置

### 2. 核心算法

#### 时间衰减算法
```
decayed_score = final_score × exp(-hours_ago / 24)

24小时前: 衰减至 36.8%
48小时前: 衰减至 13.5%
72小时前: 衰减至 5.0%
```

#### 多空幅度计算
- 使用 sigmoid 函数防止幅度通胀
- 大多数值映射到 20-80% 区间
- 避免 90%+ 或 10%- 的极端值泛滥

### 3. 配置项详解

#### 相关性配置
- **关注行业**: 多选，如"人工智能"、"量化交易"
- **关键词**: 带权重值（1-10），用于相关度匹配
- **排除词**: 包含这些词的新闻会被过滤

#### 多空配置
- **多空敏感度**: 0.1-3.0，调节多空判断的严格程度
  - 低(0.1-0.5): 保守，只有强信号才判断多空
  - 正常(1.0): 平衡
  - 高(2.0-3.0): 敏感，轻微信号也会判断

- **影响维度权重**: 市场/行业/政策/技术各维度的重要性
  - 权重越高，该维度在综合评分中占比越大

- **影响时间范围**: short/medium/long
  - 影响分析时会侧重不同时间尺度的影响

- **关键词多空配置**: 每个关键词可设置
  - 多空倾向: bullish(利多) / bearish(利空) / neutral(中性)
  - 影响幅度: 0-100%

### 4. 数据结构

#### NewsFeedItem (信息流)
```typescript
{
  id: number
  title: string              // 标题
  brief_summary: string      // 简短摘要(200字)
  brief_impact: string       // 一句话影响(100字)
  position_bias: 'bullish' | 'bearish' | 'neutral'
  position_magnitude: number // 多空幅度0-100%
  decayed_score: number      // 时间衰减后评分
  final_score: number        // 原始综合评分
  source: string             // 来源名称
  source_url: string         // 来源链接
  time_ago: string           // "3小时前"
  keywords: string[]
  categories: string[]
}
```

#### NewsDetail (详情)
```typescript
{
  // 基础信息
  id, title, content, url, source, author, published_at...
  
  // 评分
  final_score: number
  position_bias: string
  position_magnitude: number
  
  // 多维度影响
  impact_analysis: {
    market: { score, analysis(150字), bias, magnitude }
    industry: { score, analysis(150字), bias, magnitude }
    policy: { score, analysis(150字), bias, magnitude }
    tech: { score, analysis(150字), bias, magnitude }
  }
  
  // 维度权重(来自用户配置)
  relevance_weights: { market, industry, policy, tech }
}
```

## 启动步骤

### 1. 后端初始化

```bash
cd backend

# 1. 运行数据库迁移(添加新字段)
python scripts/migrate_add_position_fields.py

# 2. 初始化默认配置
python scripts/init_default_config.py

# 3. 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端启动

```bash
cd frontend

# 1. 安装依赖(如果尚未安装)
npm install

# 2. 启动开发服务器
npm run dev
```

### 3. 访问应用

- 首页(信息流): http://localhost:3000
- 新闻详情: 点击任意信息块
- 配置管理: http://localhost:3000/config

## API端点

### 信息流相关

```
GET /api/v1/news/feed
参数: limit=20, offset=0
响应: { items: NewsFeedItem[], total: number, has_more: boolean }

GET /api/v1/news/{news_id}/detail
响应: NewsDetail
```

### 配置相关

```
GET /api/v1/config/user
响应: UserConfig

PUT /api/v1/config/user
参数: UserConfig
响应: UserConfig
```

## 注意事项

1. **旧数据**: 已存在的新闻数据不会自动计算多空影响，新爬取的新闻会自动生成
2. **默认配置**: 首次启动时请运行初始化脚本创建默认配置
3. **数据库**: SQLite数据库会自动创建，生产环境建议迁移到PostgreSQL
4. **类型错误**: 代码中的部分LSP类型警告是误报，不影响实际运行

## 后续优化建议

1. 添加实时推送通知（WebSocket）
2. 实现用户自定义排序偏好
3. 添加信息收藏/标记功能
4. 实现多用户支持和权限管理
5. 添加数据可视化图表
