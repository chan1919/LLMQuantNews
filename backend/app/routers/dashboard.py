from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.services.news_service import NewsService, CostService
from app.models import News
from app.schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_dashboard_stats(
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取仪表盘统计数据"""
    from sqlalchemy import func
    
    # 确定查询日期
    if date:
        # 解析传入的日期字符串 (格式: YYYY-MM-DD)
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            # 如果日期格式错误，使用当天
            target_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        # 默认使用当天
        target_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 计算次日日期（用于范围查询）
    next_date = target_date + timedelta(days=1)
    
    # 总体统计
    total_news = db.query(func.count(News.id)).scalar() or 0
    total_pushed = db.query(func.count(News.id)).filter(News.is_pushed == True).scalar() or 0
    
    # 指定日期统计
    date_news = db.query(func.count(News.id)).filter(
        News.crawled_at >= target_date,
        News.crawled_at < next_date
    ).scalar() or 0
    
    date_pushed = db.query(func.count(News.id)).filter(
        News.is_pushed == True,
        News.last_push_at >= target_date,
        News.last_push_at < next_date
    ).scalar() or 0
    
    # 指定日期的平均分数
    date_avg_score = db.query(func.avg(News.final_score)).filter(
        News.crawled_at >= target_date,
        News.crawled_at < next_date
    ).scalar() or 0
    
    # 成本统计
    total_cost = CostService.get_cost_summary(db, days=365).get('total_cost_usd', 0)
    monthly_cost = CostService.get_monthly_cost(db)
    
    # 活跃爬虫数
    from app.services.news_service import CrawlerService
    active_crawlers = len(CrawlerService.get_active_configs(db))
    
    # 指定日期的新闻
    date_news_list = db.query(News).filter(
        News.crawled_at >= target_date,
        News.crawled_at < next_date
    ).order_by(News.crawled_at.desc()).limit(5).all()
    
    return {
        "total_news": total_news,
        "today_news": date_news,
        "total_pushed": total_pushed,
        "today_pushed": date_pushed,
        "avg_score": round(date_avg_score, 2),
        "total_cost_usd": total_cost,
        "monthly_cost_usd": monthly_cost,
        "active_crawlers": active_crawlers,
        "recent_news": [news.to_dict() for news in date_news_list]
    }

@router.get("/trends")
async def get_news_trends(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """获取新闻趋势"""
    from sqlalchemy import func
    
    trends = []
    for i in range(days):
        date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        next_date = date + timedelta(days=1)
        
        count = db.query(func.count(News.id)).filter(
            News.crawled_at >= date,
            News.crawled_at < next_date
        ).scalar() or 0
        
        avg_score = db.query(func.avg(News.final_score)).filter(
            News.crawled_at >= date,
            News.crawled_at < next_date
        ).scalar() or 0
        
        trends.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": count,
            "avg_score": round(avg_score, 2)
        })
    
    return {"trends": list(reversed(trends))}
