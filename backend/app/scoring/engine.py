from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math

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


def calculate_decayed_score(final_score: float, crawled_at: datetime, half_life_hours: float = 24.0) -> float:
    """计算时间衰减后的评分
    
    使用指数衰减公式：decayed_score = final_score * exp(-hours_ago / half_life_hours)
    默认24小时半衰期
    
    Args:
        final_score: 原始综合评分
        crawled_at: 抓取时间
        half_life_hours: 半衰期（小时）
    
    Returns:
        时间衰减后的评分
    """
    if not crawled_at:
        return final_score
    
    if isinstance(crawled_at, str):
        try:
            # 处理ISO格式日期字符串
            import re
            date_str = re.sub(r'Z$', '+00:00', crawled_at)
            crawled_at = datetime.fromisoformat(date_str)
        except Exception:
            return final_score
    
    hours_ago = (datetime.utcnow() - crawled_at).total_seconds() / 3600
    decay_factor = math.exp(-hours_ago / half_life_hours)
    decayed_score = final_score * decay_factor
    
    return round(decayed_score, 2)


def calculate_position_bias(
    sentiment: str,
    market_impact: float,
    keyword_matches: List[Dict[str, Any]],
    keyword_positions: Dict[str, Dict[str, Any]],
    sensitivity: float = 1.0
) -> Tuple[str, float]:
    """计算多空判断和幅度
    
    Args:
        sentiment: AI情感分析结果 (positive/negative/neutral)
        market_impact: 市场影响力评分
        keyword_matches: 匹配的关键词列表
        keyword_positions: 用户配置的关键词多空设置
        sensitivity: 多空敏感度调节系数
    
    Returns:
        (bias, magnitude) - bias: bullish/bearish/neutral, magnitude: 0-100%
    """
    # 基础分数计算
    base_score = 50.0  # 中性基准
    
    # 1. 情感分析贡献
    sentiment_scores = {
        'positive': 70,
        'negative': 30,
        'neutral': 50
    }
    sentiment_score = sentiment_scores.get(sentiment, 50)
    base_score = base_score * 0.3 + sentiment_score * 0.7
    
    # 2. 市场影响力贡献（影响力越大，多空越显著）
    market_contribution = (market_impact - 50) * 0.3
    base_score += market_contribution
    
    # 3. 关键词多空配置贡献
    keyword_bias_score = 0
    keyword_weight = 0
    
    for match in keyword_matches:
        keyword = match.get('keyword', '')
        if keyword in keyword_positions:
            pos_config = keyword_positions[keyword]
            bias = pos_config.get('bias', 'neutral')
            magnitude = pos_config.get('magnitude', 50)
            
            # bullish增加分数，bearish减少分数
            if bias == 'bullish':
                keyword_bias_score += magnitude
            elif bias == 'bearish':
                keyword_bias_score -= magnitude
            keyword_weight += 1
    
    if keyword_weight > 0:
        avg_keyword_bias = keyword_bias_score / keyword_weight
        base_score += avg_keyword_bias * 0.4
    
    # 应用敏感度调节
    adjusted_score = 50 + (base_score - 50) * sensitivity
    
    # 归一化到0-100范围
    adjusted_score = max(0, min(100, adjusted_score))
    
    # 判断多空方向
    if adjusted_score >= 55:
        bias = 'bullish'
    elif adjusted_score <= 45:
        bias = 'bearish'
    else:
        bias = 'neutral'
    
    # 计算幅度 - 使用sigmoid函数避免通胀，将大多数值映射到20-80区间
    distance_from_neutral = abs(adjusted_score - 50)
    # Sigmoid: 100 / (1 + exp(-x/20 + 2))
    magnitude = 100 / (1 + math.exp(-distance_from_neutral / 15 + 2))
    magnitude = round(max(0, min(100, magnitude)), 1)
    
    return bias, magnitude


def generate_impact_analysis(
    ai_scores: Dict[str, float],
    news_item: Dict[str, Any],
    dimension_weights: Dict[str, float],
    position_bias: str,
    position_magnitude: float
) -> Dict[str, Any]:
    """生成多维度影响分析
    
    Args:
        ai_scores: AI评分结果
        news_item: 新闻数据
        dimension_weights: 用户配置的维度权重
        position_bias: 多空判断
        position_magnitude: 多空幅度
    
    Returns:
        各维度影响分析字典
    """
    title = news_item.get('title', '')
    content = news_item.get('content', '')[:500]  # 取前500字符
    
    # 计算各维度分数（基于AI评分和规则）
    market_score = ai_scores.get('market_impact', 50)
    industry_score = ai_scores.get('industry_relevance', 50)
    
    # 政策维度 - 基于关键词匹配
    policy_keywords = ['政策', '监管', '法规', '央行', '政府', '税收', '补贴']
    policy_score = 50
    for keyword in policy_keywords:
        if keyword in title or keyword in content:
            policy_score = min(90, policy_score + 15)
    
    # 技术维度 - 基于关键词匹配
    tech_keywords = ['技术', '算法', 'AI', '人工智能', '模型', '创新', '突破']
    tech_score = 50
    for keyword in tech_keywords:
        if keyword in title or keyword in content:
            tech_score = min(90, tech_score + 15)
    
    # 生成简短影响描述（限150字）
    def generate_brief_analysis(dimension: str, score: float) -> str:
        """生成维度的简短影响分析"""
        if score >= 80:
            level = "重大影响"
        elif score >= 60:
            level = "明显影响"
        elif score >= 40:
            level = "一般影响"
        else:
            level = "轻微影响"
        
        bias_desc = {
            'bullish': '利好',
            'bearish': '利空',
            'neutral': '中性'
        }.get(position_bias, '中性')
        
        return f"该信息对{dimension}产生{level}，整体偏向{bias_desc}方向，建议关注后续发展。"[:150]
    
    analysis = {
        'market': {
            'score': round(market_score, 1),
            'analysis': generate_brief_analysis('市场', market_score),
            'bias': position_bias,
            'magnitude': position_magnitude
        },
        'industry': {
            'score': round(industry_score, 1),
            'analysis': generate_brief_analysis('行业', industry_score),
            'bias': position_bias,
            'magnitude': position_magnitude
        },
        'policy': {
            'score': round(policy_score, 1),
            'analysis': generate_brief_analysis('政策', policy_score),
            'bias': position_bias,
            'magnitude': position_magnitude
        },
        'tech': {
            'score': round(tech_score, 1),
            'analysis': generate_brief_analysis('技术', tech_score),
            'bias': position_bias,
            'magnitude': position_magnitude
        }
    }
    
    return analysis


def get_time_ago(crawled_at: datetime) -> str:
    """获取相对时间描述"""
    if not crawled_at:
        return "未知"
    
    if isinstance(crawled_at, str):
        try:
            # 处理ISO格式日期字符串
            date_str = crawled_at.replace('Z', '+00:00') if crawled_at.endswith('Z') else crawled_at
            crawled_at = datetime.fromisoformat(date_str)
        except Exception:
            return "未知"
    
    now = datetime.utcnow()
    diff = now - crawled_at
    
    if diff.days > 0:
        return f"{diff.days}天前"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}小时前"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}分钟前"
    else:
        return "刚刚"


def generate_brief_impact(
    title: str,
    position_bias: str,
    position_magnitude: float,
    dimension_scores: Dict[str, float]
) -> str:
    """生成一句话简短影响描述
    
    Args:
        title: 新闻标题
        position_bias: 多空判断
        position_magnitude: 多空幅度
        dimension_scores: 各维度评分
    
    Returns:
        限100字的影响描述
    """
    bias_desc = {
        'bullish': '利多',
        'bearish': '利空',
        'neutral': '中性'
    }.get(position_bias, '中性')
    
    # 找出最高影响的维度
    top_dimension = max(dimension_scores.items(), key=lambda x: x[1])
    dimension_names = {
        'market': '市场',
        'industry': '行业',
        'policy': '政策',
        'tech': '技术'
    }
    
    impact_desc = f"对{dimension_names.get(top_dimension[0], '相关领域')}有"
    
    if position_magnitude >= 70:
        strength = "显著"
    elif position_magnitude >= 40:
        strength = "一定"
    else:
        strength = "轻微"
    
    brief = f"{impact_desc}{strength}{bias_desc}影响，幅度约{position_magnitude:.0f}%"
    return brief[:100]
