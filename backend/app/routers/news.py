from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import News
from app.schemas import (
    NewsResponse, NewsListResponse, NewsCreate, NewsUpdate, NewsFilter,
    DashboardStats
)
from app.services.news_service import NewsService

router = APIRouter(prefix="/news", tags=["news"])

@router.get("", response_model=NewsListResponse)
async def list_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    min_score: Optional[float] = Query(None, ge=0, le=100),
    max_score: Optional[float] = Query(None, ge=0, le=100),
    is_pushed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """获取新闻列表"""
    filters = NewsFilter(
        source=source,
        keyword=keyword,
        category=category,
        min_score=min_score,
        max_score=max_score,
        is_pushed=is_pushed
    )
    
    news_list, total = NewsService.get_news_list(db, skip=skip, limit=limit, filters=filters)
    
    return {
        "items": [item.to_dict() for item in news_list],
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }

@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(news_id: int, db: Session = Depends(get_db)):
    """获取单条新闻详情"""
    news = NewsService.get_news_by_id(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news.to_dict()

@router.post("", response_model=NewsResponse)
async def create_news(news_data: NewsCreate, db: Session = Depends(get_db)):
    """创建新闻（手动添加）"""
    news = NewsService.create_news(db, news_data)
    return news.to_dict()

@router.put("/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int, 
    news_data: NewsUpdate, 
    db: Session = Depends(get_db)
):
    """更新新闻"""
    news = NewsService.update_news(db, news_id, news_data)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news.to_dict()

@router.delete("/{news_id}")
async def delete_news(news_id: int, db: Session = Depends(get_db)):
    """删除新闻"""
    success = NewsService.delete_news(db, news_id)
    if not success:
        raise HTTPException(status_code=404, detail="News not found")
    return {"message": "News deleted successfully"}

@router.get("/sources/list")
async def get_sources(db: Session = Depends(get_db)):
    """获取所有新闻来源"""
    sources = NewsService.get_sources(db)
    return {"sources": sources}

@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有分类"""
    categories = NewsService.get_categories(db)
    return {"categories": categories}
