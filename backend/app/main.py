from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, get_db
from app.routers import api_router
from app.services.news_service import NewsService, CostService
from app.models import News

# 创建数据库表
Base.metadata.create_all(bind=engine)

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# 定时任务，定期推送数据
async def periodic_push():
    while True:
        try:
            # 获取数据库会话
            db = next(get_db())
            
            # 获取仪表盘统计数据
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            # 今日统计
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_news = db.query(func.count(News.id)).filter(News.crawled_at >= today).scalar() or 0
            today_pushed = db.query(func.count(News.id)).filter(
                News.is_pushed == True,
                News.last_push_at >= today
            ).scalar() or 0
            
            # 最近新闻
            recent_news = db.query(News).order_by(News.crawled_at.desc()).limit(5).all()
            recent_news_list = [news.to_dict() for news in recent_news]
            
            # 构建消息
            message = {
                "type": "dashboard_update",
                "data": {
                    "today_news": today_news,
                    "today_pushed": today_pushed,
                    "recent_news": recent_news_list
                }
            }
            
            # 广播消息
            await manager.broadcast(message)
            
        except Exception as e:
            print(f"Error in periodic push: {e}")
        
        # 每30秒推送一次
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print(f"Starting {settings.APP_NAME}...")
    
    # 启动定时推送任务
    task = asyncio.create_task(periodic_push())
    
    yield
    
    # 关闭时执行
    task.cancel()
    print(f"Shutting down {settings.APP_NAME}...")

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered news aggregation and analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")

# WebSocket端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
