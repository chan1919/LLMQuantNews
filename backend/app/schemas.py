from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class PositionBias(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class NewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = None
    url: str = Field(..., max_length=2000)
    source: str = Field(..., max_length=100)
    source_type: str = Field(default="web", max_length=50)
    author: Optional[str] = Field(None, max_length=200)
    published_at: Optional[datetime] = None

class NewsCreate(NewsBase):
    pass

class NewsUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    summary: Optional[str] = None
    is_pushed: Optional[bool] = None

class NewsResponse(NewsBase):
    id: int
    summary: Optional[str] = None
    crawled_at: datetime
    ai_score: float
    market_impact: float
    industry_relevance: float
    novelty_score: float
    urgency: float
    keywords: List[str]
    categories: List[str]
    sentiment: Optional[Sentiment]
    final_score: float
    is_pushed: bool
    pushed_to: List[str]
    llm_model_used: Optional[str]
    
    class Config:
        from_attributes = True

class NewsListResponse(BaseModel):
    items: List[NewsResponse]
    total: int
    page: int
    page_size: int

class NewsFilter(BaseModel):
    source: Optional[str] = None
    keyword: Optional[str] = None
    category: Optional[str] = None
    min_score: Optional[float] = Field(None, ge=0, le=100)
    max_score: Optional[float] = Field(None, ge=0, le=100)
    is_pushed: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None



class CrawlerType(str, Enum):
    RSS = "rss"
    WEB = "web"
    API = "api"
    CUSTOM = "custom"

class CrawlerConfigBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    crawler_type: CrawlerType
    source_url: Optional[str] = Field(None, max_length=2000)
    is_active: bool = True
    interval_seconds: int = Field(default=300, ge=60)
    priority: int = Field(default=5, ge=1, le=10)
    custom_config: Dict[str, Any] = Field(default_factory=dict)
    custom_script: Optional[str] = None

class CrawlerConfigCreate(CrawlerConfigBase):
    pass

class CrawlerConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    source_url: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None
    interval_seconds: Optional[int] = Field(None, ge=60)
    priority: Optional[int] = Field(None, ge=1, le=10)
    custom_config: Optional[Dict[str, Any]] = None
    custom_script: Optional[str] = None

class CrawlerConfigResponse(CrawlerConfigBase):
    id: int
    last_crawled_at: Optional[datetime]
    last_success_at: Optional[datetime]
    last_error: Optional[str]
    total_crawled: int
    success_count: int
    error_count: int
    # 有效性状态
    is_valid: Optional[bool] = None
    last_test_at: Optional[datetime] = None
    test_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LLMCostResponse(BaseModel):
    id: int
    created_at: datetime
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    cost_cny: float
    request_type: Optional[str]
    news_id: Optional[int]
    duration_ms: Optional[int]
    status: str
    
    class Config:
        from_attributes = True

class CostSummary(BaseModel):
    total_requests: int
    total_tokens: int
    by_model: Dict[str, Dict[str, Any]]

class PushTestRequest(BaseModel):
    channel: str = Field(..., pattern="^(feishu|email)$")
    test_content: str = "这是一条测试消息"

class AITaskType(str, Enum):
    SUMMARIZE = "summarize"
    CLASSIFY = "classify"
    SCORE = "score"
    EXTRACT_KEYWORDS = "extract_keywords"
    SENTIMENT = "sentiment"
    TRANSLATE = "translate"

class AITaskRequest(BaseModel):
    content: str = Field(..., min_length=10)
    tasks: List[AITaskType] = Field(default_factory=list)
    model: Optional[str] = None

class AITaskResponse(BaseModel):
    summary: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    sentiment: Optional[Sentiment] = None
    scores: Dict[str, float] = Field(default_factory=dict)
    cost: Optional[LLMCostResponse] = None
    processing_time_ms: int

class DashboardStats(BaseModel):
    total_news: int
    today_news: int
    total_pushed: int
    today_pushed: int
    avg_score: float
    total_requests: int
    total_tokens: int
    active_crawlers: int
    recent_news: List[NewsResponse]

class ImpactDimension(BaseModel):
    """影响维度数据"""
    score: float = Field(..., ge=0, le=100)
    analysis: str = Field(..., max_length=150)  # 限150字
    bias: PositionBias
    magnitude: float = Field(..., ge=0, le=100)  # 0-100%

class NewsFeedItem(BaseModel):
    """信息流列表项"""
    id: int
    title: str
    brief_summary: str = Field(..., max_length=200)  # 简短摘要
    brief_impact: str = Field(default="", max_length=100)  # 一句话影响
    position_bias: PositionBias
    position_magnitude: float = Field(..., ge=0, le=100)  # 多空幅度%
    decayed_score: float  # 时间衰减后评分
    final_score: float  # 原始综合评分
    user_relevance_score: float = Field(default=0.0)  # 用户相关度评分
    source: str
    source_url: str
    published_at: datetime
    crawled_at: datetime
    time_ago: str  # "3小时前"
    keywords: List[str]
    categories: List[str]
    # AI分析数据
    ai_score: float = Field(default=0.0)
    market_impact: float = Field(default=0.0)
    industry_relevance: float = Field(default=0.0)
    novelty_score: float = Field(default=0.0)
    urgency: float = Field(default=0.0)
    sentiment: Optional[Sentiment] = None
    is_analyzed: bool = Field(default=False)
    analyzed_at: Optional[datetime] = None
    # 时间维度多空分析
    position_time_analysis: Optional[Dict[str, Any]] = None  # short/medium/long term analysis
    
    class Config:
        from_attributes = True

class FeedListResponse(BaseModel):
    """信息流列表响应"""
    items: List[NewsFeedItem]
    total: int
    has_more: bool

class TimeHorizonAnalysis(BaseModel):
    """时间维度分析"""
    bias: PositionBias
    magnitude: float = Field(..., ge=0, le=100)
    duration: str  # "1-3天", "1-4周", "1-6月"
    key_factors: List[str] = Field(default_factory=list)

class PositionDriver(BaseModel):
    """多空驱动因素"""
    factor: str
    impact: float = Field(..., ge=-100, le=100)  # 正负影响值
    probability: float = Field(..., ge=0, le=1)

class TradingSignal(BaseModel):
    """交易信号"""
    action: str  # 买入、卖出、增持、减持、观望等
    target: str  # 目标板块/资产
    urgency: str  # high/medium/low
    rationale: str = Field(default="", max_length=200)

class PositionAnalysisDetail(BaseModel):
    """详细多空分析"""
    overall: Dict[str, Any]  # bias, magnitude, confidence
    by_sector: List[Dict[str, Any]]  # sector, bias, magnitude
    by_asset: List[Dict[str, Any]]  # asset, bias, magnitude  
    time_horizon: Dict[str, TimeHorizonAnalysis]  # short_term, medium_term, long_term
    key_drivers: List[PositionDriver]
    trading_signals: List[TradingSignal]

class CausalEvent(BaseModel):
    """因果链事件"""
    type: str  # trigger, cause, effect, implication
    entity: str
    action: str
    time: Optional[str]
    confidence: float = Field(..., ge=0, le=1)
    evidence: List[str] = Field(default_factory=list)

class CausalChain(BaseModel):
    """因果逻辑链"""
    events: List[CausalEvent]
    root_cause: str
    immediate_effects: List[str]
    long_term_implications: List[str]

class NewsDetail(BaseModel):
    """新闻详情响应"""
    # 基础信息
    id: int
    title: str
    content: str
    url: str
    source: str
    source_url: str
    author: Optional[str]
    published_at: datetime
    crawled_at: datetime
    
    # 评分信息
    final_score: float
    position_bias: PositionBias
    position_magnitude: float  # 0-100%
    
    # 多维度影响分析
    impact_analysis: Dict[str, ImpactDimension]  # market/industry/policy/tech
    
    # 维度权重（基于用户配置）
    relevance_weights: Dict[str, float]
    
    # 其他信息
    keywords: List[str]
    categories: List[str]
    summary: Optional[str]
    sentiment: Optional[Sentiment]
    
    # 新增：详细分析
    causal_chain: Optional[CausalChain] = None
    position_analysis: Optional[PositionAnalysisDetail] = None
    related_news: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

class KeywordPosition(BaseModel):
    """关键词多空配置"""
    bias: PositionBias
    magnitude: float = Field(..., ge=0, le=100)  # 0-100%

class UserConfigBase(BaseModel):
    keywords: Dict[str, float] = Field(default_factory=dict)
    industries: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    excluded_keywords: List[str] = Field(default_factory=list)
    ai_weight: float = Field(default=0.6, ge=0, le=1)
    rule_weight: float = Field(default=0.4, ge=0, le=1)
    min_score_threshold: float = Field(default=60.0, ge=0, le=100)
    default_llm_model: str = Field(default="deepseek-chat", max_length=100)
    enable_ai_summary: bool = True
    enable_ai_classification: bool = True
    enable_ai_scoring: bool = True
    push_enabled: bool = True
    push_channels: List[str] = Field(default_factory=list)
    email_recipients: List[str] = Field(default_factory=list)
    
    # 新增配置
    position_sensitivity: float = Field(default=1.0, ge=0.1, le=3.0)  # 多空敏感度
    keyword_positions: Dict[str, KeywordPosition] = Field(default_factory=dict)  # 关键词多空配置
    dimension_weights: Dict[str, float] = Field(default_factory=lambda: {
        "market": 0.3,
        "industry": 0.25,
        "policy": 0.25,
        "tech": 0.2
    })
    impact_timeframe: str = Field(default="medium", pattern="^(short|medium|long)$")
    
    # 新增：自然语言配置
    user_description: Optional[str] = None
    analysis_mode: str = Field(default="keywords", pattern="^(keywords|description|hybrid)$")

class UserConfigUpdate(UserConfigBase):
    pass

class UserConfigResponse(UserConfigBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # 新增字段（只读）
    ai_generated_keywords: Dict[str, float] = Field(default_factory=dict)
    ai_generated_filters: Dict[str, Any] = Field(default_factory=dict)
    ai_generated_sources: List[str] = Field(default_factory=list)
    preferred_sources: Dict[str, float] = Field(default_factory=dict)
    blocked_sources: List[str] = Field(default_factory=list)
    pending_ai_config: Dict[str, Any] = Field(default_factory=dict)
    last_config_analysis_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
