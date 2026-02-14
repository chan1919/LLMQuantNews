<div align="center">
  <h2>LLMQuant News - 前端</h2>

  [![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
  [![MUI](https://img.shields.io/badge/MUI-5.0+-blue.svg)](https://mui.com/)
  [![Vite](https://img.shields.io/badge/Vite-5.0+-green.svg)](https://vitejs.dev/)

  React 18 + TypeScript + MUI 构建的现代化前端应用
</div>

## 📋 项目简介

LLMQuant News 前端是一个基于 React 18 和 TypeScript 构建的现代化单页应用，为用户提供直观的新闻量化分析界面，包括新闻列表、新闻详情、AI 成本分析和系统配置等功能。

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
| :--- | :--- | :--- |
| React | 18+ | 前端框架 |
| TypeScript | 5.0+ | 类型系统 |
| MUI | 5.0+ | UI 组件库 |
| Vite | 5.0+ | 构建工具 |
| React Router | 6.0+ | 路由管理 |
| Axios | - | HTTP 客户端 |
| Recharts | - | 数据可视化 |
| React Query | - | 数据获取与缓存 |

## 📁 目录结构

```
frontend/
├── src/                 # 源代码
│   ├── components/      # 通用组件
│   │   └── Layout.tsx   # 布局组件
│   ├── pages/           # 页面组件
│   │   ├── Dashboard.tsx    # 仪表盘
│   │   ├── NewsList.tsx     # 新闻列表
│   │   ├── NewsDetail.tsx   # 新闻详情
│   │   ├── FeedList.tsx     # 数据源配置
│   │   ├── Config.tsx       # 系统配置
│   │   └── Costs.tsx         # AI 成本分析
│   ├── types/           # TypeScript 类型定义
│   │   └── index.ts     # 类型导出
│   ├── App.tsx          # 应用根组件
│   └── main.tsx         # 应用入口
├── public/              # 静态资源
├── Dockerfile           # Docker 构建文件
├── nginx.conf           # Nginx 配置
├── package.json         # 项目配置和依赖
├── tsconfig.json        # TypeScript 配置
├── tsconfig.node.json   # Node.js TypeScript 配置
└── vite.config.ts       # Vite 配置
```

## 🚀 快速开始

### 环境要求

- Node.js 18.0+
- npm 9.0+ 或 yarn 1.22+

### 开发流程

1. **安装依赖**

   ```bash
   npm install
   # 或
   yarn install
   ```

2. **启动开发服务器**

   ```bash
   npm run dev
   # 或
   yarn dev
   ```

   开发服务器将在 `http://localhost:5173` 启动。

3. **代码格式化**

   ```bash
   npm run format
   # 或
   yarn format
   ```

4. **类型检查**

   ```bash
   npm run typecheck
   # 或
   yarn typecheck
   ```

## 🏗️ 构建与部署

### 构建生产版本

```bash
npm run build
# 或
yarn build
```

构建产物将生成在 `dist` 目录中。

### 使用 Docker 部署

```bash
# 构建 Docker 镜像
docker build -t llmquant-news-frontend .

# 运行容器
docker run -p 80:80 llmquant-news-frontend
```

### 使用 Docker Compose 部署

在项目根目录运行：

```bash
docker-compose up -d
```

## 🎨 代码规范

- 使用 TypeScript 进行类型定义
- 组件使用 PascalCase 命名
- 文件和目录使用 kebab-case 命名
- 函数使用 camelCase 命名
- 使用 ESLint 和 Prettier 进行代码检查和格式化

## 📡 API 接口

前端通过以下 API 与后端通信：

- **新闻相关**: `/api/news`
- **数据源相关**: `/api/feeds`
- **配置相关**: `/api/config`
- **成本相关**: `/api/costs`

详细的 API 文档可在后端 API 文档中查看：`http://localhost:8000/docs`

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进前端代码！

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](../LICENSE) 文件