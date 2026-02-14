<div align="center">
  <h2>LLMQuant News - 后端</h2>
  
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
  [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-blue.svg)](https://www.sqlalchemy.org/)
  [![Celery](https://img.shields.io/badge/Celery-5.0+-green.svg)](https://docs.celeryq.dev/)
  [![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
  
  FastAPI + SQLAlchemy + Celery 构建的高性能后端服务
</div>

## 📋 项目简介

LLMQuant News 后端是一个基于 FastAPI 构建的高性能后端服务，提供新闻采集、AI 分析、量化评分、多渠道推送等核心功能的 API 接口。

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
| :--- | :--- | :--- |
| Python | 3.10+ | 编程语言 |
| FastAPI | 0.100+ | Web 框架 |
| SQLAlchemy | 2.0+ | ORM 框架 |
| Celery | 5.0+ | 分布式任务队列 |
| Redis | 7.0+ | 缓存和消息代理 |
| SQLite | 3.0+ | 关系型数据库 |
| LiteLLM | - | 统一 LLM 模型接口 |
| Pydantic | 2.0+ | 数据验证 |
| Uvicorn | - | ASGI 服务器 |

## 📁 目录结构

```
backend/
├── app/                 # 主应用目录
│   ├── crawler/         # 爬虫模块
│   │   ├── base.py      # 基础爬虫类
│   │   ├── rss_crawler.py # RSS 爬虫
│   │   ├── web_crawler.py # 网页爬虫
│   │   ├── api_crawler.py # API 爬虫
│   │   ├── custom_crawler.py # 自定义爬虫
│   │   └── manager.py   # 爬虫管理器
│   ├── llm/             # LLM 模块
│   │   └── engine.py    # LLM 引擎
│   ├── push/            # 推送模块
│   │   ├── base.py      # 基础推送类
│   │   ├── email.py     # 邮件推送
│   │   ├── feishu.py    # 飞书推送
│   │   └── manager.py   # 推送管理器
│   ├── routers/         # API 路由
│   │   ├── news.py      # 新闻相关接口
│   │   ├── ai.py        # AI 相关接口
│   │   ├── costs.py     # 成本相关接口
│   │   ├── config.py    # 配置相关接口
│   │   ├── dashboard.py # 仪表盘相关接口
│   │   └── push.py      # 推送相关接口
│   ├── scoring/         # 评分模块
│   │   └── engine.py    # 评分引擎
│   ├── services/        # 服务层
│   │   ├── celery_app.py # Celery 应用
│   │   └── news_service.py # 新闻服务
│   ├── config.py        # 应用配置
│   ├── database.py      # 数据库配置
│   ├── main.py          # 应用入口
│   ├── models.py        # 数据模型
│   └── schemas.py       # 数据传输对象
├── scripts/             # 辅助脚本
│   ├── add_news_sources.py # 添加新闻源
│   ├── init_default_config.py # 初始化默认配置
│   └── test_news_sources.py # 测试新闻源
├── tests/               # 测试目录
│   └── crawler/         # 爬虫测试
├── Dockerfile           # Docker 构建文件
└── requirements.txt     # 依赖文件
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Redis 7.0+ (用于 Celery 消息代理)

### 开发流程

1. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**

   ```bash
   # 复制环境变量示例文件
   cp .env.example .env
   # 编辑 .env 文件，填入必要的 API 密钥
   ```

3. **启动 Redis** (用于 Celery)

   ```bash
   # 如果你使用 Docker
   docker run -d -p 6379:6379 redis
   ```

4. **启动 Celery  worker**

   ```bash
   celery -A app.services.celery_app worker --loglevel=info
   ```

5. **启动开发服务器**

   ```bash
   uvicorn app.main:app --reload
   ```

   开发服务器将在 `http://localhost:8000` 启动。

6. **访问 API 文档**

   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### 初始化数据

运行初始化脚本添加默认新闻源和配置：

```bash
# 添加默认新闻源
python scripts/add_news_sources.py

# 初始化默认配置
python scripts/init_default_config.py
```

## 📡 API 接口

### 核心接口

| 模块 | 路径 | 方法 | 功能 |
| :--- | :--- | :--- | :--- |
| **新闻** | `/api/news` | GET | 获取新闻列表 |
| | `/api/news/{id}` | GET | 获取新闻详情 |
| | `/api/news` | POST | 创建新闻 |
| | `/api/news/{id}` | PUT | 更新新闻 |
| | `/api/news/{id}` | DELETE | 删除新闻 |
| **AI** | `/api/ai/analyze` | POST | 分析新闻 |
| | `/api/ai/models` | GET | 获取可用模型 |
| **成本** | `/api/costs` | GET | 获取成本统计 |
| | `/api/costs/daily` | GET | 获取每日成本 |
| **配置** | `/api/config` | GET | 获取配置 |
| | `/api/config` | PUT | 更新配置 |
| **仪表盘** | `/api/dashboard/stats` | GET | 获取仪表盘统计 |
| **推送** | `/api/push/test` | POST | 测试推送 |
| | `/api/push/settings` | GET | 获取推送设置 |
| | `/api/push/settings` | PUT | 更新推送设置 |

## 🔧 核心功能

### 1. 爬虫系统

- **多类型爬虫**：支持 RSS、网页、API 和自定义爬虫
- **定时采集**：通过 Celery 定时任务自动采集新闻
- **智能去重**：基于内容和 URL 的双重去重机制
- **失败重试**：自动重试失败的采集任务

### 2. AI 分析系统

- **多模型支持**：集成 100+ LLM 模型
- **统一接口**：使用 LiteLLM 统一调用接口
- **智能分析**：自动分析新闻内容，提取关键信息
- **成本控制**：详细的 API 调用成本追踪

### 3. 评分系统

- **双重评分**：AI 评分 + 自定义规则评分
- **多维度分析**：从多个维度对新闻进行评分
- **实时更新**：评分结果实时更新

### 4. 推送系统

- **多渠道支持**：飞书、邮件、WebSocket
- **个性化设置**：基于用户偏好的个性化推送
- **实时推送**：重要新闻实时推送

### 5. 成本管理

- **详细统计**：API 调用成本详细统计
- **预算控制**：设置 API 调用预算，避免超额
- **成本分析**：分析不同模型和任务的成本

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定模块测试
python -m pytest tests/crawler/
```

### 测试覆盖率

```bash
python -m pytest --cov=app tests/
```

## 🏗️ 构建与部署

### 使用 Docker 部署

1. **构建 Docker 镜像**

   ```bash
   docker build -t llmquant-news-backend .
   ```

2. **运行容器**

   ```bash
   docker run -d -p 8000:8000 llmquant-news-backend
   ```

### 使用 Docker Compose 部署

在项目根目录运行：

```bash
docker-compose up -d
```

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](../LICENSE) 文件