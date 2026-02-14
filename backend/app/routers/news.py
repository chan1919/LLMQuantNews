from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import News, UserConfig
from app.schemas import (
    NewsResponse, NewsListResponse, NewsCreate, NewsUpdate, NewsFilter,
    FeedListResponse, NewsDetail, DashboardStats
)
from app.services.news_service import NewsService
from app.scoring.engine import (
    calculate_decayed_score, calculate_position_bias, 
    generate_impact_analysis, get_time_ago, generate_brief_impact
)

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


@router.get("/feed", response_model=FeedListResponse)
async def get_news_feed(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """获取信息流列表（按时间衰减排序）"""
    # 获取用户配置（使用默认配置）
    user_config = db.query(UserConfig).filter(UserConfig.user_id == "default").first()
    if not user_config:
        user_config = UserConfig()
    
    # 获取新闻列表
    news_list = db.query(News).order_by(News.crawled_at.desc()).limit(200).all()
    
    # 计算时间衰减评分并排序
    feed_items = []
    for news in news_list:
        decayed_score = calculate_decayed_score(
            news.final_score or 0, 
            news.crawled_at
        )
        
        # 获取时间描述
        time_ago = get_time_ago(news.crawled_at)
        
        # 准备简短摘要（从前200字符）
        brief_summary = ""
        if news.summary:
            brief_summary = news.summary[:200]
        elif news.content:
            brief_summary = news.content[:200]
        
        # 准备简短影响
        brief_impact = news.brief_impact or "暂无影响分析"
        
        feed_items.append({
            "id": news.id,
            "title": news.title,
            "brief_summary": brief_summary,
            "brief_impact": brief_impact,
            "position_bias": news.position_bias or "neutral",
            "position_magnitude": news.position_magnitude or 0,
            "decayed_score": decayed_score,
            "final_score": news.final_score or 0,
            "source": news.source or "未知来源",
            "source_url": news.url or "",
            "published_at": news.published_at or news.crawled_at,
            "crawled_at": news.crawled_at,
            "time_ago": time_ago,
            "keywords": news.keywords or [],
            "categories": news.categories or []
        })
    
    # 按衰减后评分排序
    feed_items.sort(key=lambda x: x["decayed_score"], reverse=True)
    
    # 分页
    total = len(feed_items)
    paginated_items = feed_items[offset:offset + limit]
    has_more = (offset + limit) < total
    
    return {
        "items": paginated_items,
        "total": total,
        "has_more": has_more
    }


@router.get("/{news_id}/detail", response_model=NewsDetail)
async def get_news_detail(
    news_id: int,
    db: Session = Depends(get_db)
):
    """获取新闻详情（含个性化影响分析）"""
    news = NewsService.get_news_by_id(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # 获取用户配置
    user_config = db.query(UserConfig).filter(UserConfig.user_id == "default").first()
    if not user_config:
        user_config = UserConfig()
    
    # 准备维度权重
    dimension_weights = user_config.dimension_weights or {
        "market": 0.3,
        "industry": 0.25,
        "policy": 0.25,
        "tech": 0.2
    }
    
    # 准备影响分析
    impact_analysis = news.impact_analysis or {}
    if not impact_analysis:
        # 如果没有预先生成的影响分析，则实时生成
        ai_scores = {
            'market_impact': news.market_impact or 50,
            'industry_relevance': news.industry_relevance or 50
        }
        impact_analysis = generate_impact_analysis(
            ai_scores,
            news.to_dict(),
            dimension_weights,
            news.position_bias or "neutral",
            news.position_magnitude or 0
        )
    
    return {
        "id": news.id,
        "title": news.title,
        "content": news.content or "",
        "url": news.url or "",
        "source": news.source or "未知来源",
        "source_url": news.url or "",
        "author": news.author,
        "published_at": news.published_at or news.crawled_at,
        "crawled_at": news.crawled_at,
        "final_score": news.final_score or 0,
        "position_bias": news.position_bias or "neutral",
        "position_magnitude": news.position_magnitude or 0,
        "impact_analysis": impact_analysis,
        "relevance_weights": dimension_weights,
        "keywords": news.keywords or [],
        "categories": news.categories or [],
        "summary": news.summary,
        "sentiment": news.sentiment
    }
