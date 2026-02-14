<div align="center">
  <svg width="200" height="200" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- 背景 -->
    <rect width="200" height="200" rx="20" fill="#f0f4f8"/>
    <!-- 地球/新闻图标 -->
    <circle cx="100" cy="100" r="60" fill="#3b82f6" fill-opacity="0.8"/>
    <circle cx="100" cy="100" r="40" fill="white" fill-opacity="0.9"/>
    <!-- 新闻纸张 -->
    <path d="M70 80 L130 80 L135 120 L65 120 Z" fill="#ffffff" stroke="#333333" stroke-width="2"/>
    <path d="M80 90 L120 90" stroke="#333333" stroke-width="1.5"/>
    <path d="M80 100 L115 100" stroke="#333333" stroke-width="1.5"/>
    <!-- AI 图标 -->
    <circle cx="100" cy="70" r="12" fill="#10b981"/>
    <path d="M94 70 L106 70 M100 64 L100 76" stroke="white" stroke-width="2" stroke-linecap="round"/>
  </svg>
  
  # LLMQuant News - AI新闻量化分析平台
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
  [![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
  [![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
  
  智能新闻采集、AI分析、量化评分、多渠道推送的一站式解决方案。
</div>

## 🚀 功能特性

### 核心功能

- **多渠道新闻采集** 📡
  - 支持RSS、网页爬虫、API接口和自定义脚本
  - 定时自动采集，确保信息实时性

- **多AI模型支持** 🤖
  - 集成100+ LLM模型（OpenAI、Claude、Gemini、DeepSeek等）
  - 统一接口管理，灵活切换模型

- **智能量化评分** ⭐
  - AI评分 + 自定义规则双重评分机制
  - 多维度分析，确保评分准确性

- **多渠道推送** 📤
  - 飞书、邮件、WebSocket实时推送
  - 个性化推送设置，按需接收

- **AI成本管理** 💰
  - 详细的API调用成本追踪和控制
  - 智能预算管理，避免超额支出

- **数据永久归档** 📚
  - 支持历史数据检索和分析
  - 数据可视化，洞察趋势变化

## 🛠️ 技术栈

| 分类 | 技术 | 版本 |
| :--- | :--- | :--- |
| **前端** | React + TypeScript + MUI | 18+ |
| **后端** | FastAPI + SQLAlchemy + Celery | - |
| **AI** | LiteLLM | - |
| **数据库** | SQLite + Redis | - |
| **部署** | Docker + Docker Compose | - |

## 📦 快速开始

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

### 本地开发

#### 后端开发

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload
```

#### 前端开发

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📁 项目结构

```
llmquant-news/
├── backend/           # FastAPI后端
│   ├── app/           # 应用代码
│   ├── requirements.txt # 依赖文件
│   └── main.py        # 入口文件
├── frontend/          # React前端
│   ├── src/           # 源代码
│   ├── public/        # 静态资源
│   └── package.json   # 项目配置
├── crawler_scripts/   # 自定义爬虫脚本
├── docker-compose.yml # Docker配置
└── .env.example       # 环境变量示例
```

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📞 联系

如有问题，请通过以下方式联系我们：

- 邮箱: contact@llmquant.news
- GitHub: [LLMQuant News](https://github.com/llmquant/news)
