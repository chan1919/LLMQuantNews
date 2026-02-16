#!/usr/bin/env python3
"""
新闻筛选服务
根据用户配置对新闻进行筛选和排序
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_
from app.models import News, UserConfig, CrawlerConfig
import math

class NewsFilterService:
    """新闻筛选服务"""
    
    @staticmethod
    def calculate_user_relevance(news: News, user_config: UserConfig) -> float:
        """
        计算新闻与用户的关联度
        
        Returns:
            0-100的分数，越高表示越相关
        """
        score = 0.0
        total_weight = 0.0
        
        # 1. 关键词匹配 (权重40%)
        if user_config.keywords:
            keyword_score = 0.0
            news_text = f"{news.title} {news.content or ''} {news.summary or ''}".lower()
            news_keywords = [k.lower() for k in (news.keywords or [])]
            
            for keyword, weight in user_config.keywords.items():
                keyword_lower = keyword.lower()
                if keyword_lower in news_text:
                    # 标题匹配权重翻倍
                    if keyword_lower in news.title.lower():
                        keyword_score += weight * 2
                    else:
                        keyword_score += weight
                elif keyword_lower in news_keywords:
                    keyword_score += weight * 0.5
            
            # 归一化到0-100
            max_possible = sum(user_config.keywords.values()) * 2
            if max_possible > 0:
                keyword_score = min(100, (keyword_score / max_possible) * 100)
            
            score += keyword_score * 0.4
            total_weight += 0.4
        
        # 2. 行业匹配 (权重30%)
        if user_config.industries and news.categories:
            industry_score = 0.0
            for industry in user_config.industries:
                if any(industry.lower() in cat.lower() for cat in news.categories):
                    industry_score += 1.0
            
            if user_config.industries:
                industry_score = min(100, (industry_score / len(user_config.industries)) * 100)
            
            score += industry_score * 0.3
            total_weight += 0.3
        
        # 3. 分类匹配 (权重20%)
        if user_config.categories and news.categories:
            category_score = 0.0
            for category in user_config.categories:
                if any(category.lower() in cat.lower() for cat in news.categories):
                    category_score += 1.0
            
            if user_config.categories:
                category_score = min(100, (category_score / len(user_config.categories)) * 100)
            
            score += category_score * 0.2
            total_weight += 0.2
        
        # 4. 来源偏好 (权重10%)
        if user_config.preferred_sources and news.source:
            source_weight = user_config.preferred_sources.get(news.source, 1.0)
            # 将权重映射到0-100
            source_score = min(100, source_weight * 50)  # 1.0 -> 50, 2.0 -> 100
            score += source_score * 0.1
            total_weight += 0.1
        
        # 如果没有任何配置，返回基础分50
        if total_weight == 0:
            return 50.0
        
        # 根据实际权重归一化
        final_score = score / total_weight
        
        # 5. 排除关键词惩罚 (-30分)
        if user_config.excluded_keywords:
            news_text = f"{news.title} {news.content or ''}".lower()
            for excluded in user_config.excluded_keywords:
                if excluded.lower() in news_text:
                    final_score -= 30
                    break  # 只惩罚一次
        
        # 6. 屏蔽来源
        if user_config.blocked_sources and news.source in user_config.blocked_sources:
            final_score = 0
        
        return max(0, min(100, final_score))
    
    @staticmethod
    def calculate_time_decay_score(news: News, decay_hours: int = 24) -> float:
        """
        计算时间衰减分数
        
        Args:
            news: 新闻对象
            decay_hours: 半衰期（小时）
            
        Returns:
            衰减系数 0.0-1.0
        """
        if not news.published_at:
            return 0.5  # 无发布时间，中等衰减
        
        hours_ago = (datetime.utcnow() - news.published_at).total_seconds() / 3600
        # 指数衰减: e^(-hours/decay_hours)
        decay_factor = math.exp(-hours_ago / decay_hours)
        
        return max(0.1, decay_factor)  # 最小保留10%
    
    @staticmethod
    def filter_news_by_config(
        db: Session,
        user_config: UserConfig,
        mode: str = "important",  # "all", "important", "high_impact", "unread"
        min_score: Optional[float] = None,
        position_filter: Optional[str] = None,
        show_excluded: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[News]:
        """
        根据用户配置筛选新闻
        
        Args:
            db: 数据库会话
            user_config: 用户配置
            mode: 筛选模式
            min_score: 最低分数阈值
            position_filter: 多空筛选 (bullish/bearish/neutral)
            show_excluded: 是否显示被排除的新闻
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            筛选后的新闻列表
        """
        # 基础查询
        query = db.query(News)
        
        # 1. 屏蔽来源过滤
        if user_config.blocked_sources:
            query = query.filter(not_(News.source.in_(user_config.blocked_sources)))
        
        # 2. 最低分数阈值
        threshold = min_score if min_score is not None else user_config.min_score_threshold
        
        # 3. 多空筛选
        if position_filter and position_filter != "all":
            query = query.filter(News.position_bias == position_filter)
        
        # 4. 根据模式筛选
        if mode == "important":
            # 只显示重要新闻（高分）
            query = query.filter(News.final_score >= threshold)
        elif mode == "high_impact":
            # 高影响新闻
            query = query.filter(News.market_impact >= 80)
        
        # 5. 时间范围（默认最近7天）
        week_ago = datetime.utcnow() - timedelta(days=7)
        query = query.filter(News.published_at >= week_ago)
        
        # 6. 排序：先按综合分数，再按发布时间
        query = query.order_by(News.final_score.desc(), News.published_at.desc())
        
        # 7. 分页
        news_list = query.offset(offset).limit(limit * 2).all()  # 多取一些用于后续筛选
        
        # 8. 计算用户相关度并再次筛选
        filtered_news = []
        for news in news_list:
            relevance = NewsFilterService.calculate_user_relevance(news, user_config)
            
            # 如果不显示被排除的，且相关度为0，则跳过
            if not show_excluded and relevance == 0:
                continue
            
            # 附加相关度分数（供前端显示）
            news.user_relevance_score = relevance
            
            filtered_news.append(news)
            
            if len(filtered_news) >= limit:
                break
        
        return filtered_news
    
    @staticmethod
    def get_feed_items(
        db: Session,
        user_config: UserConfig,
        mode: str = "important",
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取信息流列表项
        
        Returns:
            格式化的信息流列表
        """
        news_list = NewsFilterService.filter_news_by_config(
            db, user_config, mode=mode, limit=limit, offset=offset
        )
        
        feed_items = []
        for news in news_list:
            # 计算时间衰减分数
            decay_factor = NewsFilterService.calculate_time_decay_score(news)
            decayed_score = news.final_score * decay_factor
            
            # 计算"多久前"
            time_ago = NewsFilterService._format_time_ago(news.published_at)
            
            # 多空时间分析（简化版）
            position_time_analysis = NewsFilterService._get_position_time_analysis(news)
            
            item = {
                "id": news.id,
                "title": news.title,
                "brief_summary": news.summary[:200] if news.summary else news.title[:200],
                "brief_impact": news.brief_impact or "",
                "position_bias": news.position_bias or "neutral",
                "position_magnitude": news.position_magnitude or 0,
                "decayed_score": round(decayed_score, 2),
                "final_score": round(news.final_score, 2),
                "user_relevance_score": round(getattr(news, 'user_relevance_score', 0), 2),
                "source": news.source,
                "source_url": news.url,
                "published_at": news.published_at.isoformat() if news.published_at else None,
                "crawled_at": news.crawled_at.isoformat() if news.crawled_at else None,
                "time_ago": time_ago,
                "keywords": news.keywords or [],
                "categories": news.categories or [],
                "ai_score": news.ai_score or 0,
                "market_impact": news.market_impact or 0,
                "industry_relevance": news.industry_relevance or 0,
                "novelty_score": news.novelty_score or 0,
                "urgency": news.urgency or 0,
                "sentiment": news.sentiment,
                "is_analyzed": news.is_analyzed,
                "analyzed_at": news.analyzed_at.isoformat() if news.analyzed_at else None,
                "position_time_analysis": position_time_analysis
            }
            
            feed_items.append(item)
        
        return feed_items
    
    @staticmethod
    def _format_time_ago(published_at: Optional[datetime]) -> str:
        """格式化时间为'多久前'"""
        if not published_at:
            return "未知时间"
        
        now = datetime.utcnow()
        diff = now - published_at
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "刚刚"
        elif seconds < 3600:
            return f"{int(seconds/60)}分钟前"
        elif seconds < 86400:
            return f"{int(seconds/3600)}小时前"
        elif seconds < 604800:
            return f"{int(seconds/86400)}天前"
        else:
            return published_at.strftime("%m-%d")
    
    @staticmethod
    def _get_position_time_analysis(news: News) -> Dict[str, Any]:
        """获取多空时间分析"""
        if news.position_analysis:
            return news.position_analysis.get("time_horizon", {})
        
        # 简化版：基于整体多空判断和时间推算
        bias = news.position_bias or "neutral"
        magnitude = news.position_magnitude or 0
        
        return {
            "short_term": {
                "bias": bias,
                "magnitude": magnitude,
                "duration": "1-3天"
            },
            "medium_term": {
                "bias": bias,
                "magnitude": max(0, magnitude - 10),
                "duration": "1-4周"
            },
            "long_term": {
                "bias": "neutral",
                "magnitude": max(0, magnitude - 20),
                "duration": "1-6月"
            }
        }

# 创建全局实例
news_filter_service = NewsFilterService()
