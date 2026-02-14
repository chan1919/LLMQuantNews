/**
 * 新闻信息流相关类型定义
 */

export type PositionBias = 'bullish' | 'bearish' | 'neutral';

export interface NewsFeedItem {
  id: number;
  title: string;
  brief_summary: string;
  brief_impact: string;
  position_bias: PositionBias;
  position_magnitude: number;  // 0-100%
  decayed_score: number;
  final_score: number;
  source: string;
  source_url: string;
  published_at: string;
  crawled_at: string;
  time_ago: string;
  keywords: string[];
  categories: string[];
  // AI分析数据
  ai_score: number;
  market_impact: number;
  industry_relevance: number;
  novelty_score: number;
  urgency: number;
  sentiment: 'positive' | 'negative' | 'neutral';
  is_analyzed: boolean;
  analyzed_at?: string;
}

export interface ImpactDimension {
  score: number;
  analysis: string;
  bias: PositionBias;
  magnitude: number;  // 0-100%
}

export interface NewsDetail {
  id: number;
  title: string;
  content: string;
  url: string;
  source: string;
  source_url: string;
  author?: string;
  published_at: string;
  crawled_at: string;
  final_score: number;
  position_bias: PositionBias;
  position_magnitude: number;
  impact_analysis: {
    market: ImpactDimension;
    industry: ImpactDimension;
    policy: ImpactDimension;
    tech: ImpactDimension;
  };
  relevance_weights: Record<string, number>;
  keywords: string[];
  categories: string[];
  summary?: string;
  sentiment?: 'positive' | 'negative' | 'neutral';
}

export interface FeedListResponse {
  items: NewsFeedItem[];
  total: number;
  has_more: boolean;
}

export type TimeFrame = 'short' | 'medium' | 'long';

export interface KeywordPosition {
  bias: PositionBias;
  magnitude: number;  // 0-100%
}

export interface UserConfig {
  id?: number;
  user_id: string;
  keywords: Record<string, number>;
  industries: string[];
  categories: string[];
  excluded_keywords: string[];
  ai_weight: number;
  rule_weight: number;
  min_score_threshold: number;
  default_llm_model: string;
  enable_ai_summary: boolean;
  enable_ai_classification: boolean;
  enable_ai_scoring: boolean;
  push_enabled: boolean;
  push_channels: string[];
  email_recipients: string[];
  position_sensitivity: number;
  keyword_positions: Record<string, KeywordPosition>;
  dimension_weights: {
    market: number;
    industry: number;
    policy: number;
    tech: number;
  };
  impact_timeframe: TimeFrame;
}
