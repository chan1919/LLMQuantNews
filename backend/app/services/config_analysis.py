#!/usr/bin/env python3
"""
AI配置分析服务
将用户的自然语言描述转换为结构化的配置
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import litellm
from app.models import UserConfig
from app.config import settings

class ConfigAnalysisService:
    """配置分析服务"""
    
    def __init__(self):
        self._setup_llm()
    
    def _setup_llm(self):
        """设置LLM配置"""
        if settings.VAPI_API_KEY:
            litellm.api_base = f"{settings.VAPI_BASE_URL or 'https://api.vveai.com'}/v1"
            litellm.api_key = settings.VAPI_API_KEY
        elif settings.OPENAI_API_KEY:
            litellm.api_key = settings.OPENAI_API_KEY
    
    async def analyze_description(self, description: str, existing_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        分析用户描述并生成配置
        
        Args:
            description: 用户的自然语言描述
            existing_config: 现有配置（用于保持某些设置）
            
        Returns:
            AI生成的配置字典
        """
        # 构建提示词
        prompt = self._build_analysis_prompt(description, existing_config)
        
        # 调用AI分析
        try:
            response = await litellm.acompletion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM调用失败: {e}")
            # 返回默认配置
            return self._get_default_config()
        
        # 解析AI响应
        try:
            # 尝试直接解析JSON
            config = json.loads(content)
        except json.JSONDecodeError:
            # 如果AI返回的不是纯JSON，尝试提取JSON部分
            config = self._extract_json_from_response(content)
        
        # 验证和补充默认配置
        config = self._validate_and_fill_defaults(config)
        
        return config
    
    def _build_analysis_prompt(self, description: str, existing_config: Optional[Dict] = None) -> str:
        """构建分析提示词"""
        prompt = f"""你是一位专业的金融信息分析助手。请根据用户的描述，分析并生成适合的新闻筛选和展示配置。

## 用户描述
{description}

## 分析要求
请从以下维度进行分析并返回JSON格式的配置：

1. **关键词配置** (keywords): 
   - 提取用户关注的核心关键词
   - 为每个关键词分配权重 (0.1-1.0)
   - 包括正向关键词和排除关键词

2. **行业偏好** (industries):
   - 识别用户关注的行业领域
   - 例如: 科技、金融、新能源、医疗、消费等

3. **分类偏好** (categories):
   - 用户关注的新闻类型
   - 例如: 政策、财报、市场、技术、产品等

4. **排除关键词** (excluded_keywords):
   - 识别用户不希望看到的内容类型
   - 例如: 谣言、炒作、广告等

5. **信息源推荐** (recommended_sources):
   - 根据用户偏好推荐适合的信息源
   - 为每个源分配推荐权重 (0.0-2.0)
   - 可用源: 东方财富网、同花顺、新浪财经、中国新闻网、36氪、虎嗅网、Reuters、Bloomberg、CNBC、BBC News、Financial Times、Yahoo Finance、TechCrunch、Wired

6. **多空敏感度** (position_sensitivity):
   - 0.1-3.0 之间
   - 1.0为正常敏感度
   - 如果用户对政策/市场变化敏感，设置为1.5-2.0
   - 如果用户偏好长期持有不关心短期波动，设置为0.5-0.8

7. **时间偏好** (impact_timeframe):
   - short: 关注短期影响 (1-7天)
   - medium: 关注中期影响 (1-4周)
   - long: 关注长期影响 (1-6月)
   - 可以是列表: ["short", "medium"]

8. **关键词多空映射** (keyword_positions):
   - 某些关键词天然带有看多或看空倾向
   - 例如: "加息"→看空,"降息"→看多,"业绩超预期"→看多
   - 格式: {{"关键词": {{"bias": "bullish/bearish", "magnitude": 0.0-1.0}}}}

9. **过滤规则** (filters):
   - 内容过滤规则
   - 例如: 只关注A股、过滤市值小于100亿的公司等

## 输出格式
请严格按照以下JSON格式返回，不要添加任何其他说明文字:

{{
    "keywords": {{
        "关键词1": 0.9,
        "关键词2": 0.7
    }},
    "industries": ["行业1", "行业2"],
    "categories": ["分类1", "分类2"],
    "excluded_keywords": ["排除词1", "排除词2"],
    "recommended_sources": {{
        "源名称1": 1.5,
        "源名称2": 1.2
    }},
    "position_sensitivity": 1.2,
    "impact_timeframe": "medium",
    "keyword_positions": {{
        "关键词1": {{"bias": "bullish", "magnitude": 0.8}},
        "关键词2": {{"bias": "bearish", "magnitude": 0.7}}
    }},
    "filters": {{
        "description": "过滤规则描述"
    }},
    "analysis_reasoning": "分析理由的简要说明"
}}"""
        
        return prompt
    
    def _extract_json_from_response(self, response: str) -> Dict:
        """从AI响应中提取JSON"""
        # 尝试找到JSON的开始和结束
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            try:
                return json.loads(response[start_idx:end_idx+1])
            except:
                pass
        
        # 如果提取失败，返回空配置
        return {}
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "keywords": {"财经": 0.8, "科技": 0.7},
            "industries": ["金融", "科技"],
            "categories": ["市场", "政策"],
            "excluded_keywords": [],
            "recommended_sources": {
                "新浪财经": 1.2,
                "东方财富网": 1.2,
                "36氪": 1.0
            },
            "position_sensitivity": 1.0,
            "impact_timeframe": "medium",
            "keyword_positions": {},
            "filters": {},
            "analysis_reasoning": "使用默认配置（AI分析失败）"
        }

    def _validate_and_fill_defaults(self, config: Dict) -> Dict:
        """验证配置并填充默认值"""
        defaults = {
            "keywords": {},
            "industries": [],
            "categories": [],
            "excluded_keywords": [],
            "recommended_sources": {},
            "position_sensitivity": 1.0,
            "impact_timeframe": "medium",
            "keyword_positions": {},
            "filters": {},
            "analysis_reasoning": ""
        }
        
        # 合并默认值
        for key, value in defaults.items():
            if key not in config or config[key] is None:
                config[key] = value
        
        # 验证数值范围
        if isinstance(config.get("position_sensitivity"), (int, float)):
            config["position_sensitivity"] = max(0.1, min(3.0, config["position_sensitivity"]))
        
        # 确保impact_timeframe是字符串或列表
        timeframe = config.get("impact_timeframe", "medium")
        if isinstance(timeframe, list):
            config["impact_timeframe"] = timeframe[0] if timeframe else "medium"
        elif timeframe not in ["short", "medium", "long"]:
            config["impact_timeframe"] = "medium"
        
        return config
    
    def apply_ai_config(self, user_config: UserConfig, ai_config: Dict, confirmed: bool = True) -> UserConfig:
        """
        应用AI生成的配置
        
        Args:
            user_config: 用户配置对象
            ai_config: AI生成的配置
            confirmed: 是否已确认应用
            
        Returns:
            更新后的用户配置
        """
        if not confirmed:
            # 保存到待确认配置
            user_config.pending_ai_config = ai_config
            user_config.analysis_mode = "description"
            return user_config
        
        # 应用配置
        user_config.analysis_mode = "description"
        user_config.user_description = ai_config.get("description", "")
        
        # 合并关键词（保留用户原有的，添加AI生成的）
        existing_keywords = user_config.keywords or {}
        ai_keywords = ai_config.get("keywords", {})
        user_config.keywords = {**existing_keywords, **ai_keywords}
        user_config.ai_generated_keywords = ai_keywords
        
        # 设置行业和分类
        if ai_config.get("industries"):
            user_config.industries = list(set(user_config.industries or []) | set(ai_config["industries"]))
        if ai_config.get("categories"):
            user_config.categories = list(set(user_config.categories or []) | set(ai_config["categories"]))
        
        # 排除关键词
        if ai_config.get("excluded_keywords"):
            user_config.excluded_keywords = list(set(user_config.excluded_keywords or []) | set(ai_config["excluded_keywords"]))
        
        # AI推荐的源
        user_config.ai_generated_sources = list(ai_config.get("recommended_sources", {}).keys())
        user_config.preferred_sources = ai_config.get("recommended_sources", {})
        
        # 设置参数
        user_config.position_sensitivity = ai_config.get("position_sensitivity", 1.0)
        user_config.impact_timeframe = ai_config.get("impact_timeframe", "medium")
        
        # 关键词多空映射
        if ai_config.get("keyword_positions"):
            user_config.keyword_positions = {**user_config.keyword_positions, **ai_config["keyword_positions"]}
        
        # AI生成的过滤规则
        user_config.ai_generated_filters = ai_config.get("filters", {})
        
        # 更新时间
        user_config.last_config_analysis_at = datetime.utcnow()
        user_config.pending_ai_config = {}  # 清空待确认配置
        
        return user_config
    
    def get_recommended_sources(self, industries: List[str], categories: List[str]) -> Dict[str, float]:
        """
        根据行业和分类推荐信息源
        
        Args:
            industries: 关注行业列表
            categories: 关注分类列表
            
        Returns:
            推荐的源及其权重
        """
        # 源的行业匹配度映射
        source_industry_mapping = {
            "东方财富网": ["金融", "财经", "股票"],
            "同花顺": ["金融", "财经", "股票"],
            "新浪财经": ["综合", "财经", "科技"],
            "中国新闻网": ["综合", "政策", "国内"],
            "36氪": ["科技", "创业", "互联网"],
            "虎嗅网": ["科技", "商业", "互联网"],
            "Reuters": ["国际", "财经", "宏观"],
            "Bloomberg": ["国际", "财经", "市场"],
            "CNBC": ["国际", "财经", "市场"],
            "BBC News": ["国际", "综合"],
            "Financial Times": ["国际", "财经", "深度"],
            "Yahoo Finance": ["国际", "财经", "市场"],
            "TechCrunch": ["科技", "创新", "创业"],
            "Wired": ["科技", "深度", "趋势"],
        }
        
        recommended = {}
        
        for source, source_industries in source_industry_mapping.items():
            score = 0.0
            
            # 计算行业匹配度
            for industry in industries:
                if industry in source_industries:
                    score += 0.3
            
            # 计算分类匹配度
            for category in categories:
                if category in source_industries:
                    score += 0.2
            
            if score > 0:
                # 基础权重1.0 + 匹配得分
                recommended[source] = min(2.0, 1.0 + score)
        
        # 按权重排序
        return dict(sorted(recommended.items(), key=lambda x: x[1], reverse=True))

# 创建全局实例
config_analysis_service = ConfigAnalysisService()
