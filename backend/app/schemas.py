from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
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

class UserConfigBase(BaseModel):
    keywords: Dict[str, float] = Field(default_factory=dict)
    industries: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    excluded_keywords: List[str] = Field(default_factory=list)
    ai_weight: float = Field(default=0.6, ge=0, le=1)
    rule_weight: float = Field(default=0.4, ge=0, le=1)
    min_score_threshold: float = Field(default=60.0, ge=0, le=100)
    default_llm_model: str = Field(default="gpt-4o", max_length=100)
    enable_ai_summary: bool = True
    enable_ai_classification: bool = True
    enable_ai_scoring: bool = True
    push_enabled: bool = True
    push_channels: List[str] = Field(default_factory=list)
    email_recipients: List[str] = Field(default_factory=list)

class UserConfigUpdate(UserConfigBase):
    pass

class UserConfigResponse(UserConfigBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

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
    total_cost_usd: float
    total_cost_cny: float
    total_requests: int
    total_tokens: int
    by_model: Dict[str, Dict[str, float]]
    by_day: List[Dict[str, Any]]

class PushTestRequest(BaseModel):
    channel: str = Field(..., regex="^(feishu|email)$")
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
    total_cost_usd: float
    monthly_cost_usd: float
    active_crawlers: int
    recent_news: List[NewsResponse]
