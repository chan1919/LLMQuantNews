from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ScoreWeights:
    """评分权重配置"""
    ai_weight: float = 0.6
    rule_weight: float = 0.4
    
    # AI评分权重
    market_impact_weight: float = 0.3
    industry_relevance_weight: float = 0.25
    novelty_weight: float = 0.25
    urgency_weight: float = 0.2

class NewsScorer:
    """新闻量化评分引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weights = ScoreWeights(
            ai_weight=config.get('ai_weight', 0.6),
            rule_weight=config.get('rule_weight', 0.4),
        )
        self.keywords = config.get('keywords', {})
        self.industries = config.get('industries', [])
        self.categories = config.get('categories', [])
        self.excluded_keywords = config.get('excluded_keywords', [])
    
    def calculate_final_score(
        self, 
        ai_scores: Dict[str, float],
        news_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        计算最终综合评分
        
        总分 = AI评分 * AI权重 + 规则评分 * 规则权重
        """
        # 1. 计算AI综合评分
        ai_score = self._calculate_ai_composite_score(ai_scores)
        
        # 2. 计算规则评分
        rule_score = self._calculate_rule_score(news_item)
        
        # 3. 加权计算最终分数
        final_score = (
            ai_score * self.weights.ai_weight + 
            rule_score * self.weights.rule_weight
        )
        
        # 确保分数在0-100范围内
        final_score = max(0, min(100, final_score))
        
        return {
            'final_score': round(final_score, 2),
            'ai_score': round(ai_score, 2),
            'rule_score': round(rule_score, 2),
            'breakdown': {
                'ai_component': ai_scores,
                'rule_details': self._get_rule_details(news_item),
            },
            'factors': {
                'ai_weight': self.weights.ai_weight,
                'rule_weight': self.weights.rule_weight,
            }
        }
    
    def _calculate_ai_composite_score(self, ai_scores: Dict[str, float]) -> float:
        """计算AI综合评分"""
        if not ai_scores:
            return 50.0  # 默认中等分数
        
        # 加权平均
        weighted_sum = (
            ai_scores.get('market_impact', 50) * self.weights.market_impact_weight +
            ai_scores.get('industry_relevance', 50) * self.weights.industry_relevance_weight +
            ai_scores.get('novelty_score', 50) * self.weights.novelty_weight +
            ai_scores.get('urgency', 50) * self.weights.urgency_weight
        )
        
        return weighted_sum
    
    def _calculate_rule_score(self, news_item: Dict[str, Any]) -> float:
        """基于规则的评分"""
        score = 0
        
        # 1. 关键词匹配评分
        title = news_item.get('title', '').lower()
        content = news_item.get('content', '').lower()[:2000]  # 只检查前2000字符
        full_text = f"{title} {content}"
        
        for keyword, weight in self.keywords.items():
            keyword_lower = keyword.lower()
            if keyword_lower in title:
                score += weight * 2  # 标题匹配权重更高
            elif keyword_lower in content:
                score += weight
        
        # 2. 行业匹配
        news_categories = news_item.get('categories', [])
        for industry in self.industries:
            if industry.lower() in [c.lower() for c in news_categories]:
                score += 15
        
        # 3. 来源权重
        source_weights = {
            'reuters': 20,
            'bloomberg': 20,
            'techcrunch': 15,
            'the verge': 15,
            'arxiv': 18,
            'github': 12,
        }
        source = news_item.get('source', '').lower()
        for source_name, weight in source_weights.items():
            if source_name in source:
                score += weight
                break
        
        # 4. 时效性加分
        published_at = news_item.get('published_at')
        if published_at:
            try:
                if isinstance(published_at, str):
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                hours_ago = (datetime.utcnow() - published_at).total_seconds() / 3600
                if hours_ago < 1:
                    score += 10  # 1小时内
                elif hours_ago < 6:
                    score += 5   # 6小时内
            except:
                pass
        
        # 5. 排除关键词检查
        for excluded in self.excluded_keywords:
            if excluded.lower() in full_text:
                score -= 30  # 大幅减分
        
        return max(0, min(100, score))
    
    def _get_rule_details(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """获取规则评分详情"""
        details = {
            'keyword_matches': [],
            'industry_matches': [],
            'source_bonus': 0,
            'timeliness_bonus': 0,
            'excluded_penalty': 0,
        }
        
        title = news_item.get('title', '').lower()
        content = news_item.get('content', '').lower()
        
        # 关键词匹配详情
        for keyword, weight in self.keywords.items():
            keyword_lower = keyword.lower()
            if keyword_lower in title:
                details['keyword_matches'].append({
                    'keyword': keyword,
                    'weight': weight * 2,
                    'location': 'title'
                })
            elif keyword_lower in content:
                details['keyword_matches'].append({
                    'keyword': keyword,
                    'weight': weight,
                    'location': 'content'
                })
        
        # 行业匹配
        news_categories = news_item.get('categories', [])
        for industry in self.industries:
            if industry.lower() in [c.lower() for c in news_categories]:
                details['industry_matches'].append(industry)
        
        # 来源检查
        source_weights = {
            'reuters': 20, 'bloomberg': 20, 'techcrunch': 15,
            'the verge': 15, 'arxiv': 18, 'github': 12,
        }
        source = news_item.get('source', '').lower()
        for source_name, weight in source_weights.items():
            if source_name in source:
                details['source_bonus'] = weight
                break
        
        # 时效性
        published_at = news_item.get('published_at')
        if published_at:
            try:
                if isinstance(published_at, str):
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                hours_ago = (datetime.utcnow() - published_at).total_seconds() / 3600
                if hours_ago < 1:
                    details['timeliness_bonus'] = 10
                elif hours_ago < 6:
                    details['timeliness_bonus'] = 5
            except:
                pass
        
        # 排除关键词
        for excluded in self.excluded_keywords:
            if excluded.lower() in title or excluded.lower() in content:
                details['excluded_penalty'] = 30
                break
        
        return details
    
    def should_push(self, final_score: float) -> bool:
        """判断是否达到推送阈值"""
        threshold = self.config.get('min_score_threshold', 60)
        return final_score >= threshold
    
    def get_priority(self, final_score: float) -> str:
        """根据分数获取优先级"""
        if final_score >= 85:
            return 'high'
        elif final_score >= 70:
            return 'medium'
        else:
            return 'low'

class ScoringEngine:
    """评分引擎管理器"""
    
    def __init__(self):
        self.scorers: Dict[str, NewsScorer] = {}
    
    def create_scorer(self, user_id: str, config: Dict[str, Any]) -> NewsScorer:
        """为指定用户创建评分器"""
        scorer = NewsScorer(config)
        self.scorers[user_id] = scorer
        return scorer
    
    def get_scorer(self, user_id: str) -> Optional[NewsScorer]:
        """获取用户评分器"""
        return self.scorers.get(user_id)
    
    def score_news(
        self, 
        user_id: str, 
        ai_scores: Dict[str, float],
        news_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """对新闻进行评分"""
        scorer = self.get_scorer(user_id)
        if not scorer:
            # 使用默认配置
            scorer = NewsScorer({})
        
        return scorer.calculate_final_score(ai_scores, news_item)

# 全局评分引擎实例
scoring_engine = ScoringEngine()
