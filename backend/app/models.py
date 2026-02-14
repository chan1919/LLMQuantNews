from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import json

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), index=True, nullable=False)
    content = Column(Text)
    summary = Column(Text)
    url = Column(String(2000), unique=True, index=True)
    source = Column(String(100), index=True)  # 来源名称
    source_type = Column(String(50))  # rss, web, api, custom
    author = Column(String(200))
    published_at = Column(DateTime, index=True)
    crawled_at = Column(DateTime, default=datetime.utcnow)
    
    # AI分析结果
    ai_score = Column(Float, default=0.0)  # AI评分 0-100
    market_impact = Column(Float, default=0.0)
    industry_relevance = Column(Float, default=0.0)
    novelty_score = Column(Float, default=0.0)
    urgency = Column(Float, default=0.0)
    
    keywords = Column(JSON, default=list)  # 关键词列表
    categories = Column(JSON, default=list)  # 分类标签
    sentiment = Column(String(20))  # positive/negative/neutral
    
    # 量化评分
    rule_score = Column(Float, default=0.0)  # 规则评分
    final_score = Column(Float, default=0.0)  # 最终综合评分
    
    # 多空影响分析
    position_bias = Column(String(20))  # bullish/bearish/neutral
    position_magnitude = Column(Float, default=0.0)  # 多空幅度 0-100%
    
    # 影响维度评分
    market_impact_score = Column(Float, default=0.0)  # 市场影响 0-100
    industry_impact_score = Column(Float, default=0.0)  # 行业影响 0-100
    policy_impact_score = Column(Float, default=0.0)  # 政策影响 0-100
    tech_impact_score = Column(Float, default=0.0)  # 技术影响 0-100
    
    # 影响分析
    impact_analysis = Column(JSON, default=dict)  # 详细影响分析JSON
    brief_impact = Column(String(500))  # 一句话简短影响
    
    # LLM处理元数据
    llm_model_used = Column(String(100))  # 使用的AI模型
    processing_time_ms = Column(Integer)  # 处理耗时
    
    # 推送状态
    is_pushed = Column(Boolean, default=False)
    pushed_to = Column(JSON, default=list)  # ['feishu', 'email']
    push_attempts = Column(Integer, default=0)
    last_push_at = Column(DateTime)
    
    # 成本记录
    cost_tracking_id = Column(Integer, ForeignKey('llm_costs.id'), nullable=True)
    cost_record = relationship("LLMCost", back_populates="news_items", foreign_keys=[cost_tracking_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content[:1000] if self.content else None,  # 截断
            'summary': self.summary,
            'url': self.url,
            'source': self.source,
            'source_type': self.source_type,
            'author': self.author,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'crawled_at': self.crawled_at.isoformat() if self.crawled_at else None,
            'ai_score': self.ai_score,
            'market_impact': self.market_impact,
            'industry_relevance': self.industry_relevance,
            'novelty_score': self.novelty_score,
            'urgency': self.urgency,
            'keywords': self.keywords,
            'categories': self.categories,
            'sentiment': self.sentiment,
            'final_score': self.final_score,
            'position_bias': self.position_bias,
            'position_magnitude': self.position_magnitude,
            'market_impact_score': self.market_impact_score,
            'industry_impact_score': self.industry_impact_score,
            'policy_impact_score': self.policy_impact_score,
            'tech_impact_score': self.tech_impact_score,
            'impact_analysis': self.impact_analysis,
            'brief_impact': self.brief_impact,
            'is_pushed': self.is_pushed,
            'pushed_to': getattr(self, 'pushed_to', []),
            'llm_model_used': self.llm_model_used,
        }

class UserConfig(Base):
    __tablename__ = "user_configs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关键词配置 {"keyword": weight}
    keywords = Column(JSON, default=dict)
    
    # 关注行业
    industries = Column(JSON, default=list)
    
    # 关注分类
    categories = Column(JSON, default=list)
    
    # 排除关键词
    excluded_keywords = Column(JSON, default=list)
    
    # 评分权重配置
    ai_weight = Column(Float, default=0.6)
    rule_weight = Column(Float, default=0.4)
    min_score_threshold = Column(Float, default=60.0)
    
    # AI处理配置
    default_llm_model = Column(String(100), default="deepseek-chat")
    enable_ai_summary = Column(Boolean, default=True)
    enable_ai_classification = Column(Boolean, default=True)
    enable_ai_scoring = Column(Boolean, default=True)
    
    # 推送配置
    push_enabled = Column(Boolean, default=True)
    push_channels = Column(JSON, default=list)  # ['feishu', 'email']
    
    # 飞书配置
    feishu_webhook = Column(String(1000))
    feishu_chat_id = Column(String(100))
    
    # 邮件配置
    email_recipients = Column(JSON, default=list)
    
    # 多空敏感度配置
    position_sensitivity = Column(Float, default=1.0)  # 1.0=正常, 0.5=低敏感, 2.0=高敏感
    
    # 关键词多空配置 {"keyword": {"bias": "bullish", "magnitude": 0.8}}
    keyword_positions = Column(JSON, default=dict)
    
    # 影响维度权重
    dimension_weights = Column(JSON, default=dict)
    
    # 影响时间范围偏好
    impact_timeframe = Column(String(20), default="medium")  # short/medium/long
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'keywords': self.keywords,
            'industries': self.industries,
            'categories': self.categories,
            'excluded_keywords': self.excluded_keywords,
            'ai_weight': self.ai_weight,
            'rule_weight': self.rule_weight,
            'min_score_threshold': self.min_score_threshold,
            'default_llm_model': self.default_llm_model,
            'enable_ai_summary': self.enable_ai_summary,
            'enable_ai_classification': self.enable_ai_classification,
            'enable_ai_scoring': self.enable_ai_scoring,
            'push_enabled': self.push_enabled,
            'push_channels': self.push_channels,
            'email_recipients': self.email_recipients,
            'position_sensitivity': self.position_sensitivity,
            'keyword_positions': self.keyword_positions,
            'dimension_weights': self.dimension_weights,
            'impact_timeframe': self.impact_timeframe,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class CrawlerConfig(Base):
    __tablename__ = "crawler_configs"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    crawler_type = Column(String(50), nullable=False)  # rss, web, api, custom
    source_url = Column(String(2000))
    is_active = Column(Boolean, default=True)
    interval_seconds = Column(Integer, default=300)
    priority = Column(Integer, default=5)  # 优先级 1-10
    
    # 自定义配置
    custom_config = Column(JSON, default=dict)
    
    # 自定义脚本（用于custom类型）
    custom_script = Column(Text)
    
    # 统计
    last_crawled_at = Column(DateTime)
    last_success_at = Column(DateTime)
    last_error = Column(Text)
    total_crawled = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # 有效性状态
    is_valid = Column(Boolean, default=None)  # None: 未测试, True: 有效, False: 无效
    last_test_at = Column(DateTime)  # 最后测试时间
    test_message = Column(Text)  # 测试结果消息
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'crawler_type': self.crawler_type,
            'source_url': self.source_url,
            'is_active': self.is_active,
            'interval_seconds': self.interval_seconds,
            'priority': self.priority,
            'custom_config': self.custom_config,
            'custom_script': self.custom_script,
            'last_crawled_at': self.last_crawled_at.isoformat() if self.last_crawled_at else None,
            'last_success_at': self.last_success_at.isoformat() if self.last_success_at else None,
            'last_error': self.last_error,
            'total_crawled': self.total_crawled,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'is_valid': self.is_valid,
            'last_test_at': self.last_test_at.isoformat() if self.last_test_at else None,
            'test_message': self.test_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class LLMCost(Base):
    __tablename__ = "llm_costs"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 请求信息
    model = Column(String(100), nullable=False)
    provider = Column(String(50))
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # 成本计算
    cost_usd = Column(Float, default=0.0)
    cost_cny = Column(Float, default=0.0)  # 人民币
    
    # 请求元数据
    request_type = Column(String(50))  # summary, classify, score, etc.
    news_id = Column(Integer, ForeignKey('news.id'), nullable=True)
    duration_ms = Column(Integer)
    status = Column(String(20), default="success")  # success, error
    error_message = Column(Text)
    
    # 关联
    news_items = relationship("News", back_populates="cost_record", foreign_keys="News.cost_tracking_id")
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'model': self.model,
            'provider': self.provider,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'cost_usd': self.cost_usd,
            'cost_cny': self.cost_cny,
            'request_type': self.request_type,
            'news_id': self.news_id,
            'duration_ms': self.duration_ms,
            'status': self.status,
        }

class PushLog(Base):
    __tablename__ = "push_logs"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    news_id = Column(Integer, ForeignKey('news.id'))
    channel = Column(String(50))  # feishu, email
    status = Column(String(20))  # success, error, pending
    error_message = Column(Text)
    
    # 推送内容快照
    title = Column(String(500))
    content_preview = Column(Text)
    score = Column(Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'news_id': self.news_id,
            'channel': self.channel,
            'status': self.status,
            'title': self.title,
            'score': self.score,
        }

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    level = Column(String(20), default="info")  # debug, info, warning, error
    module = Column(String(100))
    message = Column(Text)
    details = Column(JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'level': self.level,
            'module': self.module,
            'message': self.message,
            'details': self.details,
        }
