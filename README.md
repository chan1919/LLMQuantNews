<div align="center">
  <img src="./logo.svg" alt="LLMQuant News Logo" width="200" height="200" />
  
  # LLMQuant News - AI新闻量化分析平台
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
  [![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
  [![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
  
  智能新闻采集、AI分析、量化评分、多渠道推送的一站式解决方案
</div>

---

## 📖 目录

- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [快速开始](#-快速开始)
- [配置说明](#-配置说明)
- [项目结构](#-项目结构)
- [API文档](#-api文档)
- [开发指南](#-开发指南)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## 🚀 功能特性

### 核心功能

#### 📡 多渠道新闻采集
- **RSS订阅** - 自动解析RSS/Atom Feed，支持定时更新
- **网页爬虫** - 智能提取网页内容，支持动态页面
- **API接口** - 标准化API接入，便于扩展
- **自定义脚本** - 支持Python自定义爬虫脚本

#### 🤖 多AI模型支持
- 集成 **100+ LLM模型**（OpenAI、Claude、Gemini、DeepSeek等）
- 通过 LiteLLM 统一接口管理
- 支持模型灵活切换和降级
- 智能token使用优化

#### ⭐ 智能量化评分
- **AI评分** - 基于内容重要性、时效性、影响力多维度评估
- **规则评分** - 自定义评分规则（关键词、来源权重等）
- **综合评分** - 双重评分机制加权计算
- **多空分析** - 自动分析新闻对市场的影响方向

#### 📤 多渠道推送
- **飞书推送** - 支持卡片消息、富文本格式
- **邮件推送** - SMTP协议，支持HTML邮件
- **WebSocket实时推送** - 前端实时更新
- 按评分阈值智能推送，避免信息过载

#### 💰 AI成本管理
- 详细的API调用成本追踪
- 按月/按日成本统计
- 预算超限自动告警
- 成本可视化图表

#### 📚 数据永久归档
- 历史数据永久存储
- 支持全文检索
- 数据趋势可视化
- 支持数据导出

#### ⚙️ 灵活配置管理
- **信息源管理** - 可视化配置新闻源
- **AI配置** - 模型选择、评分规则配置
- **推送配置** - 渠道开关、阈值设置
- **热点分析** - AI驱动的配置优化建议

---

## 🛠️ 技术栈

### 后端
| 技术 | 版本 | 用途 |
|:-----|:-----|:-----|
| FastAPI | 0.104.1 | Web框架 |
| SQLAlchemy | 2.0.23 | ORM |
| Celery | 5.3.4 | 异步任务队列 |
| Redis | 5.0.1 | 缓存/消息队列 |
| LiteLLM | 1.10.0 | LLM统一接口 |
| Pydantic | 2.5.0 | 数据验证 |
| newspaper4k | 0.9.0 | 网页内容提取 |
| feedparser | 6.0.10 | RSS解析 |

### 前端
| 技术 | 版本 | 用途 |
|:-----|:-----|:-----|
| React | 18.2.0 | UI框架 |
| TypeScript | 5.2.2 | 类型安全 |
| Vite | 5.0.0 | 构建工具 |
| MUI | 5.14.18 | UI组件库 |
| React Query | 5.8.4 | 数据请求 |
| Zustand | 4.4.7 | 状态管理 |
| Recharts | 2.10.3 | 图表库 |

### 基础设施
| 技术 | 用途 |
|:-----|:-----|
| Docker | 容器化部署 |
| Docker Compose | 多容器编排 |
| SQLite | 开发数据库 |
| PostgreSQL | 生产数据库（可选） |

---

## 📦 快速开始

### 前置要求
- Docker & Docker Compose
- 至少一个AI模型的API密钥

### 使用Docker部署（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd llmquant-news

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的API密钥

# 3. 创建数据目录
mkdir -p data

# 4. 启动所有服务
docker-compose up -d

# 5. 查看日志
docker-compose logs -f

# 6. 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 本地开发

#### 后端开发

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export DATABASE_URL=sqlite:///./data/llmquant.db
export REDIS_URL=redis://localhost:6379/0

# 启动Redis（需要预先安装）
redis-server

# 启动Celery Worker（新终端）
celery -A app.services.celery_app worker --loglevel=info

# 启动Celery Beat（新终端）
celery -A app.services.celery_app beat --loglevel=info

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

---

## ⚙️ 配置说明

### 环境变量配置

复制 `.env.example` 到 `.env` 并配置以下关键参数：

#### AI模型配置（至少配置一个）
```bash
OPENAI_API_KEY=sk-xxx          # OpenAI API密钥
ANTHROPIC_API_KEY=xxx           # Claude API密钥
GOOGLE_API_KEY=xxx              # Gemini API密钥
DEEPSEEK_API_KEY=xxx            # DeepSeek API密钥
DEFAULT_LLM_MODEL=gpt-4         # 默认使用的模型
```

#### 推送配置
```bash
# 飞书配置
FEISHU_APP_ID=xxx
FEISHU_APP_SECRET=xxx
ENABLE_FEISHU_PUSH=true

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASS=xxx
ENABLE_EMAIL_PUSH=true

# 推送阈值（评分高于此值才推送）
SCORE_THRESHOLD=60
```

#### 成本控制
```bash
ENABLE_COST_TRACKING=true
MONTHLY_BUDGET_USD=100          # 月度预算上限
```

### 信息源配置

在Web界面的"配置"页面可以：
1. 添加新的RSS源或网页源
2. 设置爬取频率
3. 配置源权重和过滤规则
4. 启用/禁用信息源

---

## 📁 项目结构

```
llmquant-news/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── models.py          # SQLAlchemy模型
│   │   ├── schemas.py         # Pydantic模型
│   │   ├── routers/           # API路由
│   │   │   ├── news.py        # 新闻接口
│   │   │   ├── config.py      # 配置接口
│   │   │   ├── costs.py       # 成本统计
│   │   │   ├── push.py        # 推送管理
│   │   │   └── dashboard.py   # 仪表盘数据
│   │   ├── services/          # 业务逻辑
│   │   │   ├── news_service.py
│   │   │   ├── celery_app.py  # Celery配置
│   │   │   └── tasks.py       # 异步任务
│   │   ├── crawler/           # 爬虫模块
│   │   │   ├── base.py        # 爬虫基类
│   │   │   ├── rss_crawler.py # RSS爬虫
│   │   │   ├── web_crawler.py # 网页爬虫
│   │   │   └── manager.py     # 爬虫管理器
│   │   ├── llm/               # LLM处理
│   │   │   ├── engine.py      # LLM引擎
│   │   │   └── vapi_service.py
│   │   ├── scoring/           # 评分引擎
│   │   │   └── engine.py
│   │   └── push/              # 推送模块
│   │       ├── feishu.py      # 飞书推送
│   │       └── email.py       # 邮件推送
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── main.tsx           # 应用入口
│   │   ├── App.tsx            # 根组件
│   │   ├── pages/             # 页面组件
│   │   │   ├── Dashboard.tsx  # 仪表盘
│   │   │   ├── NewsList.tsx   # 新闻列表
│   │   │   ├── NewsDetail.tsx # 新闻详情
│   │   │   ├── Config.tsx     # 配置管理
│   │   │   └── Costs.tsx      # 成本统计
│   │   └── components/        # 可复用组件
│   ├── package.json
│   └── Dockerfile
├── crawler_scripts/            # 自定义爬虫脚本
├── data/                       # 数据存储（git忽略）
├── docker-compose.yml          # Docker编排配置
├── .env.example                # 环境变量示例
├── AGENTS.md                   # AI开发指南
└── README.md                   # 项目文档
```

---

## 📚 API文档

启动服务后访问以下地址：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

| 方法 | 路径 | 描述 |
|:-----|:-----|:-----|
| GET | `/api/v1/news` | 获取新闻列表 |
| GET | `/api/v1/news/{id}` | 获取新闻详情 |
| POST | `/api/v1/news` | 创建新闻 |
| GET | `/api/v1/config/sources` | 获取信息源配置 |
| POST | `/api/v1/config/sources` | 添加信息源 |
| GET | `/api/v1/costs/stats` | 获取成本统计 |
| GET | `/api/v1/dashboard/stats` | 获取仪表盘数据 |
| POST | `/api/v1/push/test` | 测试推送 |

---

## 🔧 开发指南

### 代码风格

- **Python**: 使用 Black 格式化，行长度88字符
- **TypeScript**: 遵循现有代码风格
- **提交信息**: 遵循约定式提交规范

### 添加新的爬虫

1. 继承 `BaseNewsCrawler` 基类
2. 实现 `fetch()` 和 `parse()` 方法
3. 在 `crawler/manager.py` 注册爬虫
4. 在配置中添加信息源

详细说明请参阅 [AGENTS.md](./AGENTS.md)

### 运行测试

```bash
cd backend
pytest                           # 运行所有测试
pytest tests/test_crawlers.py   # 运行爬虫测试
pytest -v                        # 详细输出
```

---

## ❓ 常见问题

### Q: 如何添加新的AI模型？
A: 在 `.env` 文件中添加对应模型的API密钥，LiteLLM会自动识别。支持的模型列表：https://docs.litellm.ai/docs/providers

### Q: 推送不生效怎么办？
A: 
1. 检查 `.env` 中的推送配置是否正确
2. 确认 `ENABLE_*_PUSH` 设置为 `true`
3. 检查新闻评分是否达到 `SCORE_THRESHOLD`

### Q: 如何更改爬取频率？
A: 在配置页面的信息源管理中，可以单独设置每个源的爬取间隔（单位：秒）

### Q: 数据存储在哪里？
A: 
- SQLite数据库: `./data/llmquant.db`
- Redis数据: Docker volume `redis-data`

### Q: 如何备份数据？
```bash
# 备份SQLite数据库
cp ./data/llmquant.db ./data/llmquant.db.backup

# 备份Redis数据
docker exec llmquant-redis redis-cli SAVE
docker cp llmquant-redis:/data/dump.rdb ./redis-backup.rdb
```

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

请确保：
- 代码通过所有测试
- 遵循项目的代码风格
- 更新相关文档

---

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- 邮箱: suoni1919@gmail.com
- GitHub: [LLMQuant News](https://github.com/llmquant/news)

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [LiteLLM](https://github.com/BerriAI/litellm) - 统一的LLM接口
- [Material-UI](https://mui.com/) - React UI组件库
- [Celery](https://docs.celeryq.dev/) - 分布式任务队列

---

<div align="center">
  Made with ❤️ by LLMQuant Team
</div>
