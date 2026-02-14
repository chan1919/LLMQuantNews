# AGENTS.md - Coding Guidelines for LLMQuant News

## Project Overview

Full-stack AI news aggregation platform with intelligent scoring, multi-channel push, and cost tracking.

**Stack:**
- **Frontend:** React 18 + TypeScript + Vite + MUI + React Query + Zustand + Recharts
- **Backend:** FastAPI + SQLAlchemy + Pydantic + Celery + Redis + LiteLLM
- **Database:** SQLite (development), PostgreSQL (production-ready)
- **Deployment:** Docker + Docker Compose

---

## Build Commands

### Frontend (`./frontend/`)
```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Start dev server (port 3000)
npm run build        # Production build
npm run preview      # Preview production build
```

### Backend (`./backend/`)
```bash
cd backend
pip install -r requirements.txt   # Install dependencies

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# OR
python -m app.main

# Celery workers
celery -A app.services.celery_app worker --loglevel=info
celery -A app.services.celery_app beat --loglevel=info
```

### Docker (Full Stack)
```bash
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose logs -f backend    # View backend logs
```

---

## Lint/Format Commands

### Python Backend
```bash
cd backend

# Format with Black (line length 88 default)
black app/
black app/routers/news.py         # Single file

# Type checking (optional - add mypy to requirements)
mypy app/

# Run tests with pytest
pytest                            # Run all tests
pytest tests/test_news.py         # Run single test file
pytest tests/test_news.py::test_get_news   # Run single test
pytest -v                         # Verbose output
pytest -k "test_name"            # Run tests matching pattern
```

### Frontend
```bash
cd frontend

# TypeScript type checking
npx tsc --noEmit

# Build validation
npm run build
```

---

## Code Style Guidelines

### Python (Backend)

**Imports:**
```python
# 1. Standard library
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict, Any

# 2. Third-party
from fastapi import FastAPI, HTTPException
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, Field

# 3. Local (use absolute imports)
from app.config import settings
from app.models import News
from app.schemas import NewsResponse
```

**Naming Conventions:**
- Classes: `PascalCase` (e.g., `NewsService`, `BaseModel`)
- Functions/Methods: `snake_case` (e.g., `get_news_by_id`)
- Variables: `snake_case` (e.g., `news_list`, `config_data`)
- Constants: `SCREAMING_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- Private methods: `_leading_underscore` (e.g., `_validate_data`)

**Type Hints:**
- Always use type hints for function parameters and return types
- Use `Optional[X]` instead of `X | None` for Python < 3.10 compatibility
- Use `List[X]`, `Dict[K, V]`, `Any` from typing module

**Error Handling:**
```python
# Use try-except with specific exceptions
try:
    result = await process_data()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.exception("Unexpected error")
    raise HTTPException(status_code=500, detail="Internal error")
```

**FastAPI Patterns:**
```python
@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(
    news_id: int,                              # Path parameter
    include_content: bool = True,              # Query parameter with default
    db: Session = Depends(get_db)             # Dependency injection
):
    """Docstring describing the endpoint (in Chinese)."""
    news = NewsService.get_news_by_id(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news.to_dict()
```

**SQLAlchemy Models:**
```python
class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
```

**Pydantic Schemas:**
```python
class NewsCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = None
    
    class Config:
        from_attributes = True  # For ORM mode
```

**Service Classes:**
```python
class NewsService:
    """Business logic layer - use static methods."""
    
    @staticmethod
    def get_news_by_id(db: Session, news_id: int) -> Optional[News]:
        return db.query(News).filter(News.id == news_id).first()
```

---

### TypeScript/React (Frontend)

**Imports:**
```typescript
// 1. React/Third-party
import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

// 2. MUI components
import { Box, Typography, Button } from '@mui/material'
import { Dashboard as DashboardIcon } from '@mui/icons-material'

// 3. Local (use relative imports)
import Layout from './components/Layout'
import { useStore } from './store'
```

**Naming Conventions:**
- Components: `PascalCase` (e.g., `Dashboard`, `NewsList`)
- Functions/Variables: `camelCase` (e.g., `fetchData`, `isLoading`)
- Constants: `SCREAMING_SNAKE_CASE` or `camelCase` (e.g., `API_URL`)
- Types/Interfaces: `PascalCase` (e.g., `NewsItem`, `UserConfig`)
- Files: Match component name (e.g., `Dashboard.tsx`)

**Component Structure:**
```typescript
// Functional component with export default
export default function Dashboard() {
  // Hooks at top
  const { data, isLoading } = useQuery({...})
  const [count, setCount] = useState(0)
  
  // Handlers
  const handleClick = () => setCount(c => c + 1)
  
  // Early returns for loading states
  if (isLoading) return <LinearProgress />
  
  // Render
  return (
    <Box>
      <Typography variant="h4">Dashboard</Typography>
    </Box>
  )
}
```

**React Query Pattern:**
```typescript
const API_URL = '/api/v1'

const fetchDashboardStats = async () => {
  const { data } = await axios.get(`${API_URL}/dashboard/stats`)
  return data
}

function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: fetchDashboardStats,
  })
  // ...
}
```

**Styling:**
- Use MUI `sx` prop for inline styles
- Use `styled` API for reusable components
- Use theme colors: `theme.palette.primary.main`

**Error Handling:**
```typescript
// Use try-catch with async operations
try {
  await axios.post('/api/news', data)
} catch (error) {
  console.error('Failed to create news:', error)
  // Show user-friendly error message
}
```

---

## Project Structure

```
llmquant-news/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routers/             # API routes
│   │   │   ├── __init__.py
│   │   │   ├── news.py
│   │   │   ├── config.py
│   │   │   └── ...
│   │   ├── services/            # Business logic
│   │   │   ├── news_service.py
│   │   │   └── celery_app.py
│   │   ├── crawler/             # News crawlers
│   │   ├── llm/                 # LLM processing
│   │   ├── push/                # Push notifications
│   │   └── scoring/             # Scoring engine
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.tsx             # React entry
│   │   ├── App.tsx              # Root component
│   │   ├── components/          # Reusable components
│   │   ├── pages/               # Page components
│   │   └── store/               # Zustand stores (if any)
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── crawler_scripts/             # Custom crawler scripts
```

---

## Environment Setup

1. Copy `.env.example` to `.env` and configure:
   - Database URLs
   - AI API keys (at least one required)
   - Push configuration (Feishu/Email)

2. Create data directory:
   ```bash
   mkdir -p data
   ```

3. Run with Docker:
   ```bash
   docker-compose up -d
   ```

---

## Common Patterns

**Backend API Response:**
```python
# List endpoint
{
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
}

# Error response
raise HTTPException(status_code=404, detail="Resource not found")
```

**Frontend Data Fetching:**
- Use React Query for server state
- Use Zustand for client state
- Use axios for HTTP requests

**Database Operations:**
- Use SQLAlchemy ORM for queries
- Use transactions with `db.commit()`
- Always handle `Optional` returns

---

## 架构设计原则

### 高内聚低耦合

**高内聚：**
- 爬虫模块聚焦数据采集（`crawler/`）
- 推送模块聚焦消息推送（`push/`）
- 评分模块聚焦内容评分（`scoring/`）
- LLM模块聚焦AI处理（`llm/`）
- 各模块通过明确的接口交互，不直接操作其他模块的内部数据

**低耦合：**
- 使用依赖注入（FastAPI `Depends`）传递数据库会话
- 使用事件/消息队列进行模块间通信（Celery）
- 配置文件集中管理（`config.py`）
- 避免跨模块直接导入具体实现，优先导入抽象接口

### 爬虫开发规范

**新增爬虫必须遵循：**

1. **继承基类**
```python
from app.crawler.base import BaseNewsCrawler, NewsItem

class MyCrawler(BaseNewsCrawler):
    """自定义爬虫说明（中文）"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        # 实现数据抓取
        pass
    
    async def parse(self, raw_data: Dict[str, Any]) -> Optional[NewsItem]:
        # 实现数据解析
        pass
```

2. **注册到管理器**
```python
# app/crawler/manager.py
CRAWLER_MAP = {
    'my_crawler': MyCrawler,
}
```

3. **信息源配置格式**
```python
{
    "name": "信息源名称",
    "crawler_type": "rss|web|api|custom",
    "source_url": "https://example.com/feed",
    "interval_seconds": 300,
    "priority": 5,
    "custom_config": {
        # 爬虫特定配置
    }
}
```

### 测试模块架构

**爬虫测试位置：**
```
backend/tests/
├── __init__.py
├── conftest.py              # pytest配置
├── test_crawlers.py         # 爬虫单元测试
└── test_sources.py          # 信息源连通性测试
```

**测试规范：**
1. 每个爬虫类型必须有对应的测试类
2. 测试必须覆盖：连通性、数据解析、异常处理
3. 使用 `pytest-asyncio` 测试异步爬虫
4. 网络测试使用 `pytest.mark.network` 标记

**信息源健康检查：**
```bash
# 运行所有信息源测试
python -m pytest tests/test_sources.py -v

# 生成报告
python backend/scripts/test_all_sources.py
```

---

## Notes for Agents

- Write comments in Chinese for business logic
- Keep error messages user-friendly
- Use logging instead of print statements in production
- Test changes with `docker-compose` when possible
- Add type hints to all new functions
- Follow existing file structure and naming
- **项目收尾时使用相关skills：** 运行 `skill cleanup-project`、`skill crawler-testing`、`skill doc-update`
