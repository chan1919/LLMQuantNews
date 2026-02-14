# LLMQuant News - AI新闻量化分析平台

智能新闻采集、AI分析、量化评分、多渠道推送的一站式解决方案。

## 功能特性

- **多渠道新闻采集**: 支持RSS、网页爬虫、API接口和自定义脚本
- **多AI模型支持**: 集成100+ LLM模型（OpenAI、Claude、Gemini、DeepSeek等）
- **智能量化评分**: AI评分 + 自定义规则双重评分机制
- **多渠道推送**: 飞书、邮件、WebSocket实时推送
- **AI成本管理**: 详细的API调用成本追踪和控制
- **数据永久归档**: 支持历史数据检索和分析

## 技术栈

- **前端**: React 18 + TypeScript + MUI
- **后端**: FastAPI + SQLAlchemy + Celery
- **AI**: LiteLLM（统一多模型接口）
- **数据库**: SQLite + Redis
- **部署**: Docker + Docker Compose

## 快速开始

### 使用Docker部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd llmquant-news

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的API密钥

# 3. 启动服务
docker-compose up -d

# 4. 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
```

## 项目结构

```
llmquant-news/
├── backend/           # FastAPI后端
├── frontend/          # React前端
├── crawler_scripts/   # 自定义爬虫脚本
└── docker-compose.yml
```

## License

MIT License
