from fastapi import APIRouter

from app.routers import news, config, costs, push, dashboard, ai

api_router = APIRouter()

api_router.include_router(news.router)
api_router.include_router(config.router)
api_router.include_router(costs.router)
api_router.include_router(push.router)
api_router.include_router(dashboard.router)
api_router.include_router(ai.router)
