from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import News, UserConfig
from app.schemas import (
    NewsResponse, NewsListResponse, NewsCreate, NewsUpdate, NewsFilter,
    FeedListResponse, NewsDetail, DashboardStats
)
from app.services.news_service import NewsService
from app.services.news_filter import news_filter_service
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
    min_score: Optional[str] = Query(None),
    max_score: Optional[float] = Query(None, ge=0, le=100),
    is_pushed: Optional[bool] = None,
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取新闻列表"""
    # 处理min_score参数
    min_score_float = None
    if min_score and min_score.strip():
        try:
            min_score_float = float(min_score)
        except ValueError:
            pass
    
    filters = NewsFilter(
        source=source,
        keyword=keyword,
        category=category,
        min_score=min_score_float,
        max_score=max_score,
        is_pushed=is_pushed
    )
    
    # 构建查询
    query = db.query(News)
    
    # 应用过滤条件
    if source:
        query = query.filter(News.source == source)
    if keyword:
        query = query.filter(News.title.ilike(f"%{keyword}%"))
    if category:
        query = query.filter(News.categories.contains([category]))
    if min_score_float is not None:
        query = query.filter(News.final_score >= min_score_float)
    if max_score is not None:
        query = query.filter(News.final_score <= max_score)
    if is_pushed is not None:
        query = query.filter(News.is_pushed == is_pushed)
    if date:
        # 解析日期并过滤
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
            next_date = target_date + timedelta(days=1)
            query = query.filter(
                News.crawled_at >= target_date,
                News.crawled_at < next_date
            )
        except ValueError:
            # 日期格式错误，忽略日期过滤
            pass
    
    # 计算总数
    total = query.count()
    
    # 分页并排序
    news_list = query.order_by(News.crawled_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": [item.to_dict() for item in news_list],
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }

@router.get("/feed", response_model=FeedListResponse)
async def get_news_feed(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    mode: str = Query("important", description="筛选模式: all/important/high_impact/unread"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="最低评分"),
    position_filter: Optional[str] = Query(None, description="多空筛选: bullish/bearish/neutral"),
    show_excluded: bool = Query(False, description="是否显示被排除的新闻"),
    db: Session = Depends(get_db)
):
    """
    获取个性化信息流列表
    
    - mode=all: 显示所有新闻
    - mode=important: 只显示重要新闻（高于阈值）
    - mode=high_impact: 只显示高影响新闻
    - mode=unread: 只显示未读新闻（待实现）
    """
    # 获取用户配置
    user_config = db.query(UserConfig).filter(UserConfig.user_id == "default").first()
    if not user_config:
        user_config = UserConfig()
    
    # 使用新的筛选服务
    feed_items = news_filter_service.get_feed_items(
        db=db,
        user_config=user_config,
        mode=mode,
        limit=limit,
        offset=offset
    )
    
    # 计算总数（近似值）
    total_query = db.query(News)
    if user_config.blocked_sources:
        from sqlalchemy import not_
        total_query = total_query.filter(not_(News.source.in_(user_config.blocked_sources)))
    total = total_query.count()
    
    has_more = (offset + limit) < total
    
    return {
        "items": feed_items,
        "total": total,
        "has_more": has_more
    }

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

@router.get("/tags/list")
async def get_tags(db: Session = Depends(get_db)):
    """获取所有标签"""
    tags = NewsService.get_all_tags(db)
    return {"tags": tags}

@router.get("/tags/search")
async def search_by_tags(
    tags: List[str] = Query(..., description="标签列表"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """基于标签搜索新闻"""
    news_list = NewsService.get_news_by_tags(db, tags, skip, limit)
    return {
        "items": [item.to_dict() for item in news_list],
        "total": len(news_list),
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }

@router.get("/search")
async def search_news(
    query: str = Query(..., description="搜索查询"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """基于自然语言查询搜索新闻"""
    results = await NewsService.search_news(db, query, skip, limit)
    return {
        "items": results,
        "total": len(results),
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }

@router.post("/{news_id}/regenerate-tags")
async def regenerate_tags(
    news_id: int,
    db: Session = Depends(get_db)
):
    """重新生成新闻标签"""
    result = await NewsService.regenerate_tags(db, news_id)
    if not result:
        raise HTTPException(status_code=404, detail="News not found or failed to regenerate tags")
    return result

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
        "sentiment": news.sentiment,
        # 新增字段
        "causal_chain": news.causal_chain,
        "position_analysis": news.position_analysis,
        "related_news": []  # TODO: 实现相关新闻查找
    }
