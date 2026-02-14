from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models import News, UserConfig, CrawlerConfig, LLMCost, PushLog
from app.schemas import NewsCreate, NewsUpdate, NewsFilter
from app.llm import llm_engine
from app.scoring import scoring_engine
from app.push import push_manager
from app.config import settings

class NewsService:
    """新闻服务"""
    
    @staticmethod
    def get_news_list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[NewsFilter] = None
    ) -> tuple:
        """获取新闻列表"""
        query = db.query(News)
        
        if filters:
            if filters.source:
                query = query.filter(News.source == filters.source)
            if filters.keyword:
                query = query.filter(
                    News.title.contains(filters.keyword) | 
                    News.content.contains(filters.keyword)
                )
            if filters.category:
                query = query.filter(News.categories.contains([filters.category]))
            if filters.min_score is not None:
                query = query.filter(News.final_score >= filters.min_score)
            if filters.max_score is not None:
                query = query.filter(News.final_score <= filters.max_score)
            if filters.is_pushed is not None:
                query = query.filter(News.is_pushed == filters.is_pushed)
            if filters.start_date:
                query = query.filter(News.published_at >= filters.start_date)
            if filters.end_date:
                query = query.filter(News.published_at <= filters.end_date)
        
        total = query.count()
        news_list = query.order_by(desc(News.final_score), desc(News.published_at)).offset(skip).limit(limit).all()
        
        return news_list, total
    
    @staticmethod
    def get_news_by_id(db: Session, news_id: int) -> Optional[News]:
        """获取单条新闻"""
        return db.query(News).filter(News.id == news_id).first()
    
    @staticmethod
    async def create_news_with_tags(db: Session, news_data: NewsCreate) -> News:
        """创建新闻记录并生成标签"""
        # 创建新闻记录
        db_news = News(**news_data.model_dump())
        db.add(db_news)
        db.commit()
        db.refresh(db_news)
        
        # 生成标签
        if db_news.title and db_news.content:
            try:
                tag_result = await llm_engine.generate_tags(
                    db_news.title,
                    db_news.content
                )
                
                if tag_result and tag_result.get('tags'):
                    db_news.tags = tag_result['tags']
                    db_news.tag_generated_at = datetime.utcnow()
                    db.commit()
                    db.refresh(db_news)
                    
                # 记录成本
                if tag_result.get('input_tokens') and tag_result.get('output_tokens'):
                    cost = llm_engine.calculate_cost(
                        tag_result.get('model_used', 'gpt-4o-mini'),
                        tag_result['input_tokens'],
                        tag_result['output_tokens']
                    )
                    CostService.record_cost(
                        db,
                        model=tag_result.get('model_used', 'gpt-4o-mini'),
                        provider='openai',
                        prompt_tokens=tag_result['input_tokens'],
                        completion_tokens=tag_result['output_tokens'],
                        cost_usd=cost['cost_usd'],
                        cost_cny=cost['cost_cny'],
                        request_type='tag_generation',
                        news_id=db_news.id
                    )
            except Exception as e:
                print(f"生成标签失败: {e}")
        
        return db_news
    
    @staticmethod
    def create_news(db: Session, news_data: NewsCreate) -> News:
        """创建新闻记录"""
        # 同步版本，用于兼容现有代码
        import asyncio
        return asyncio.run(NewsService.create_news_with_tags(db, news_data))
    
    @staticmethod
    def update_news(db: Session, news_id: int, news_data: NewsUpdate) -> Optional[News]:
        """更新新闻"""
        db_news = db.query(News).filter(News.id == news_id).first()
        if db_news:
            update_data = news_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_news, key, value)
            db.commit()
            db.refresh(db_news)
        return db_news
    
    @staticmethod
    def delete_news(db: Session, news_id: int) -> bool:
        """删除新闻"""
        db_news = db.query(News).filter(News.id == news_id).first()
        if db_news:
            db.delete(db_news)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_sources(db: Session) -> List[str]:
        """获取所有新闻来源"""
        sources = db.query(News.source).distinct().all()
        return [s[0] for s in sources if s[0]]
    
    @staticmethod
    def get_categories(db: Session) -> List[str]:
        """获取所有分类"""
        all_categories = db.query(News.categories).all()
        categories_set = set()
        for cats in all_categories:
            if cats[0]:
                categories_set.update(cats[0])
        return sorted(list(categories_set))
    
    @staticmethod
    async def search_news(db: Session, query: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """基于自然语言查询搜索新闻"""
        # 获取基础新闻列表
        news_list = db.query(News).order_by(desc(News.published_at)).limit(100).all()
        
        # 转换为字典格式
        news_items = [
            {
                'id': news.id,
                'title': news.title,
                'content': news.content,
                'summary': news.summary,
                'source': news.source,
                'published_at': news.published_at.isoformat() if news.published_at else None,
                'tags': news.tags,
                'final_score': news.final_score
            }
            for news in news_list
        ]
        
        # 使用AI进行搜索
        if news_items:
            try:
                search_results = await llm_engine.search_news(query, news_items)
                return search_results[skip:skip+limit]
            except Exception as e:
                print(f"搜索失败: {e}")
        
        # 失败时返回原始列表
        return news_items[skip:skip+limit]
    
    @staticmethod
    def get_all_tags(db: Session) -> List[str]:
        """获取所有标签"""
        all_news = db.query(News.tags).all()
        tags_set = set()
        for tags in all_news:
            if tags[0]:
                tags_set.update(tags[0].keys())
        return sorted(list(tags_set))
    
    @staticmethod
    def get_news_by_tags(db: Session, tags: List[str], skip: int = 0, limit: int = 20) -> List[News]:
        """根据标签获取新闻"""
        query = db.query(News)
        
        # 筛选包含指定标签的新闻
        for tag in tags:
            query = query.filter(News.tags.contains({tag: 0}))  # 只要包含标签即可
        
        news_list = query.order_by(desc(News.final_score), desc(News.published_at)).offset(skip).limit(limit).all()
        return news_list
    
    @staticmethod
    async def regenerate_tags(db: Session, news_id: int) -> Optional[Dict[str, Any]]:
        """重新生成新闻标签"""
        news = db.query(News).filter(News.id == news_id).first()
        if not news or not news.title or not news.content:
            return None
        
        try:
            tag_result = await llm_engine.generate_tags(news.title, news.content)
            if tag_result and tag_result.get('tags'):
                news.tags = tag_result['tags']
                news.tag_generated_at = datetime.utcnow()
                db.commit()
                db.refresh(news)
                return {'tags': news.tags}
        except Exception as e:
            print(f"重新生成标签失败: {e}")
        
        return None

class ConfigService:
    """配置服务"""
    
    @staticmethod
    def get_user_config(db: Session, user_id: str = "default") -> UserConfig:
        """获取用户配置"""
        config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
        if not config:
            # 创建默认配置
            config = UserConfig(user_id=user_id)
            db.add(config)
            db.commit()
            db.refresh(config)
        return config
    
    @staticmethod
    def update_user_config(db: Session, user_id: str, config_data: Dict[str, Any]) -> UserConfig:
        """更新用户配置"""
        config = ConfigService.get_user_config(db, user_id)
        
        for key, value in config_data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        config.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(config)
        return config

class CrawlerService:
    """爬虫配置服务"""
    
    @staticmethod
    def get_all_configs(db: Session) -> List[CrawlerConfig]:
        """获取所有爬虫配置"""
        return db.query(CrawlerConfig).order_by(CrawlerConfig.priority.desc()).all()
    
    @staticmethod
    def get_active_configs(db: Session) -> List[CrawlerConfig]:
        """获取活跃的爬虫配置"""
        return db.query(CrawlerConfig).filter(CrawlerConfig.is_active == True).all()
    
    @staticmethod
    def get_config_by_id(db: Session, config_id: int) -> Optional[CrawlerConfig]:
        """获取指定配置"""
        return db.query(CrawlerConfig).filter(CrawlerConfig.id == config_id).first()
    
    @staticmethod
    def create_config(db: Session, config_data: Dict[str, Any]) -> CrawlerConfig:
        """创建爬虫配置"""
        db_config = CrawlerConfig(**config_data)
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        return db_config
    
    @staticmethod
    def update_config(db: Session, config_id: int, config_data: Dict[str, Any]) -> Optional[CrawlerConfig]:
        """更新爬虫配置"""
        db_config = db.query(CrawlerConfig).filter(CrawlerConfig.id == config_id).first()
        if db_config:
            for key, value in config_data.items():
                if hasattr(db_config, key) and key != 'id':
                    setattr(db_config, key, value)
            db_config.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_config)
        return db_config
    
    @staticmethod
    def delete_config(db: Session, config_id: int) -> bool:
        """删除爬虫配置"""
        db_config = db.query(CrawlerConfig).filter(CrawlerConfig.id == config_id).first()
        if db_config:
            db.delete(db_config)
            db.commit()
            return True
        return False
    
    @staticmethod
    def update_stats(db: Session, config_id: int, success: bool, error_msg: str = None):
        """更新爬虫统计"""
        db_config = db.query(CrawlerConfig).filter(CrawlerConfig.id == config_id).first()
        if db_config:
            db_config.last_crawled_at = datetime.utcnow()
            db_config.total_crawled += 1
            
            if success:
                db_config.last_success_at = datetime.utcnow()
                db_config.success_count += 1
            else:
                db_config.error_count += 1
                db_config.last_error = error_msg
            
            db.commit()

class CostService:
    """成本管理服务"""
    
    @staticmethod
    def record_cost(
        db: Session,
        model: str,
        provider: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        cost_cny: float,
        request_type: str,
        news_id: int = None,
        duration_ms: int = None,
        status: str = "success",
        error_message: str = None
    ) -> LLMCost:
        """记录API调用成本"""
        cost_record = LLMCost(
            model=model,
            provider=provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_usd=cost_usd,
            cost_cny=cost_cny,
            request_type=request_type,
            news_id=news_id,
            duration_ms=duration_ms,
            status=status,
            error_message=error_message
        )
        db.add(cost_record)
        db.commit()
        db.refresh(cost_record)
        return cost_record
    
    @staticmethod
    def get_cost_summary(db: Session, days: int = 30) -> Dict[str, Any]:
        """获取使用统计汇总"""
        from datetime import timedelta
        from_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        from_date = from_date - timedelta(days=days)
        
        # 总请求数
        total_requests = db.query(func.count(LLMCost.id)).filter(
            LLMCost.created_at >= from_date
        ).scalar() or 0
        
        # 总token数
        total_tokens = db.query(func.sum(LLMCost.total_tokens)).filter(
            LLMCost.created_at >= from_date
        ).scalar() or 0
        
        # 按模型统计
        by_model = db.query(
            LLMCost.model,
            func.count(LLMCost.id).label('count'),
            func.sum(LLMCost.total_tokens).label('tokens'),
            func.sum(LLMCost.prompt_tokens).label('prompt_tokens'),
            func.sum(LLMCost.completion_tokens).label('completion_tokens')
        ).filter(
            LLMCost.created_at >= from_date
        ).group_by(LLMCost.model).all()
        
        by_model_dict = {
            row.model: {
                'requests': row.count,
                'tokens': row.tokens or 0,
                'prompt_tokens': row.prompt_tokens or 0,
                'completion_tokens': row.completion_tokens or 0
            }
            for row in by_model
        }
        
        return {
            'total_requests': total_requests,
            'total_tokens': total_tokens or 0,
            'by_model': by_model_dict,
        }
    
    @staticmethod
    def get_monthly_cost(db: Session) -> float:
        """获取当月成本"""
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        cost = db.query(func.sum(LLMCost.cost_usd)).filter(
            LLMCost.created_at >= month_start
        ).scalar() or 0
        
        return round(cost, 4)
    
    @staticmethod
    def check_budget(db: Session) -> Dict[str, Any]:
        """检查预算状态"""
        monthly_cost = CostService.get_monthly_cost(db)
        budget = settings.MONTHLY_BUDGET_USD
        
        percentage = (monthly_cost / budget * 100) if budget > 0 else 0
        
        return {
            'monthly_cost_usd': monthly_cost,
            'budget_usd': budget,
            'percentage': round(percentage, 2),
            'remaining': round(budget - monthly_cost, 4),
            'status': 'danger' if percentage >= 100 else 'warning' if percentage >= 80 else 'normal'
        }

class PushService:
    """推送服务"""
    
    @staticmethod
    async def push_news(
        db: Session,
        news_item: News,
        channels: List[str],
        config: UserConfig
    ) -> Dict[str, Any]:
        """推送新闻到指定渠道"""
        news_dict = news_item.to_dict()
        
        # 构建推送配置
        push_configs = {
            'feishu': {
                'webhook': config.feishu_webhook,
                'chat_id': config.feishu_chat_id,
            },
            'email': {
                'recipients': config.email_recipients,
            }
        }
        
        # 执行推送
        results = await push_manager.push(news_dict, channels, push_configs)
        
        # 更新推送状态
        pushed_channels = []
        for channel, result in results.items():
            if result.success:
                pushed_channels.append(channel)
            
            # 记录推送日志
            push_log = PushLog(
                news_id=news_item.id,
                channel=channel,
                status='success' if result.success else 'error',
                error_message=result.error_message,
                title=news_item.title,
                content_preview=news_item.content[:500] if news_item.content else None,
                score=news_item.final_score
            )
            db.add(push_log)
        
        # 更新新闻推送状态
        if pushed_channels:
            news_item.is_pushed = True
            news_item.pushed_to = pushed_channels
            news_item.push_attempts += 1
            news_item.last_push_at = datetime.utcnow()
            db.commit()
        
        return {
            'success': len(pushed_channels) > 0,
            'pushed_to': pushed_channels,
            'results': {k: {'success': v.success, 'error': v.error_message} for k, v in results.items()}
        }
    
    @staticmethod
    async def test_push_channel(channel: str, config: Dict[str, Any]) -> bool:
        """测试推送渠道"""
        return await push_manager.test_channel(channel, config)
