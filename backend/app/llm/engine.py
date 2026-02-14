import litellm
from typing import Dict, Any, List, Optional
import time
import json
from datetime import datetime

from app.config import settings
from app.models import LLMCost
from app.llm.vapi_service import vapi_service

class LLMEngine:
    """多模型LLM处理引擎 - 基于LiteLLM"""
    
    # 支持的模型配置
    AVAILABLE_MODELS = {
        'gpt-4o': {'provider': 'openai', 'model': 'gpt-4o', 'cost_per_1k_input': 0.005, 'cost_per_1k_output': 0.015},
        'gpt-4o-mini': {'provider': 'openai', 'model': 'gpt-4o-mini', 'cost_per_1k_input': 0.00015, 'cost_per_1k_output': 0.0006},
        'claude-3-opus': {'provider': 'anthropic', 'model': 'claude-3-opus-20240229', 'cost_per_1k_input': 0.015, 'cost_per_1k_output': 0.075},
        'claude-3-sonnet': {'provider': 'anthropic', 'model': 'claude-3-sonnet-20240229', 'cost_per_1k_input': 0.003, 'cost_per_1k_output': 0.015},
        'gemini-pro': {'provider': 'gemini', 'model': 'gemini-pro', 'cost_per_1k_input': 0.0005, 'cost_per_1k_output': 0.0015},
        'deepseek-chat': {'provider': 'deepseek', 'model': 'deepseek-chat', 'cost_per_1k_input': 0.00014, 'cost_per_1k_output': 0.00028},
    }
    
    def __init__(self):
        self.default_model = settings.DEFAULT_LLM_MODEL
        self._setup_api_keys()
        self._setup_vapi()
    
    def _setup_vapi(self):
        """配置V-API"""
        if settings.VAPI_API_KEY:
            # 设置LiteLLM的V-API配置
            litellm.api_base = f"{settings.VAPI_BASE_URL or 'https://api.vveai.com'}/v1"
            litellm.api_key = settings.VAPI_API_KEY
    
    def _setup_api_keys(self):
        """配置API密钥"""
        if settings.OPENAI_API_KEY:
            litellm.api_key = settings.OPENAI_API_KEY
        # 其他密钥通过环境变量或litellm自动读取
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取所有可用模型列表"""
        return [
            {
                'id': model_id,
                'name': config['model'],
                'provider': config['provider'],
                'cost_per_1k_input': config['cost_per_1k_input'],
                'cost_per_1k_output': config['cost_per_1k_output'],
            }
            for model_id, config in self.AVAILABLE_MODELS.items()
        ]
    
    async def get_vapi_models(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """
        获取V-API支持的模型列表
        
        Args:
            refresh: 是否刷新缓存
            
        Returns:
            V-API模型列表
        """
        vapi_models = await vapi_service.get_chat_models(refresh)
        return [
            {
                'id': model.get('id'),
                'name': model.get('id'),
                'provider': model.get('owned_by', 'vapi'),
                'cost_per_1k_input': 0.0,  # V-API价格需要从API获取或配置
                'cost_per_1k_output': 0.0,
            }
            for model in vapi_models
        ]
    
    async def process_news(
        self, 
        title: str, 
        content: str,
        tasks: List[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理新闻的多任务流水线
        
        tasks: ['summarize', 'classify', 'score', 'keywords', 'sentiment']
        """
        if tasks is None:
            tasks = ['summarize', 'classify', 'score', 'keywords', 'sentiment']
        
        model = model or self.default_model
        if model not in self.AVAILABLE_MODELS:
            model = self.default_model
        
        results = {
            'model_used': model,
            'tasks_completed': [],
            'processing_time_ms': 0,
            'cost': None,
        }
        
        start_time = time.time()
        total_cost = {'input_tokens': 0, 'output_tokens': 0, 'cost_usd': 0}
        
        try:
            # 准备内容
            full_content = f"标题: {title}\n\n内容: {content[:3000]}"  # 限制长度
            
            # 1. 摘要生成
            if 'summarize' in tasks:
                summary_result = await self._summarize(full_content, model)
                results['summary'] = summary_result['text']
                results['tasks_completed'].append('summarize')
                self._accumulate_cost(total_cost, summary_result)
            
            # 2. 分类
            if 'classify' in tasks:
                classify_result = await self._classify(full_content, model)
                results['categories'] = classify_result['categories']
                results['tasks_completed'].append('classify')
                self._accumulate_cost(total_cost, classify_result)
            
            # 3. 评分（重要性、紧急度等）
            if 'score' in tasks:
                score_result = await self._score(full_content, model)
                results['scores'] = score_result['scores']
                results['tasks_completed'].append('score')
                self._accumulate_cost(total_cost, score_result)
            
            # 4. 关键词提取
            if 'keywords' in tasks:
                keyword_result = await self._extract_keywords(full_content, model)
                results['keywords'] = keyword_result['keywords']
                results['tasks_completed'].append('keywords')
                self._accumulate_cost(total_cost, keyword_result)
            
            # 5. 情感分析
            if 'sentiment' in tasks:
                sentiment_result = await self._analyze_sentiment(full_content, model)
                results['sentiment'] = sentiment_result['sentiment']
                results['tasks_completed'].append('sentiment')
                self._accumulate_cost(total_cost, sentiment_result)
            
        except Exception as e:
            results['error'] = str(e)
            results['status'] = 'error'
        
        end_time = time.time()
        results['processing_time_ms'] = int((end_time - start_time) * 1000)
        results['cost'] = total_cost
        
        return results
    
    async def _summarize(self, content: str, model: str) -> Dict[str, Any]:
        """生成摘要"""
        prompt = f"""请为以下新闻生成一段简洁的摘要（100字以内）：

{content}

请直接返回摘要内容，不要添加任何其他文字。"""
        
        # 使用V-API模型
        response = await litellm.acompletion(
            model="openai/gpt-4o-mini",  # 使用完整的模型路径
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
        )
        
        return {
            'text': response.choices[0].message.content.strip(),
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens,
        }
    
    async def _classify(self, content: str, model: str) -> Dict[str, Any]:
        """分类新闻"""
        prompt = f"""请将以下新闻分类（可多选），返回JSON格式：

{content}

可选分类：["财经", "科技", "AI", "区块链", "政策", "市场", "公司", "国际", "社会"]

返回格式：{{"categories": ["分类1", "分类2"]}}"""
        
        # 使用V-API模型
        response = await litellm.acompletion(
            model="openai/gpt-4o-mini",  # 使用完整的模型路径
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100,
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            categories = result.get('categories', [])
        except:
            categories = []
        
        return {
            'categories': categories,
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens,
        }
    
    async def _score(self, content: str, model: str) -> Dict[str, Any]:
        """多维度评分"""
        prompt = f"""请评估以下新闻的各个维度（0-100分），返回JSON格式：

{content}

评估维度：
1. 市场影响度：对金融市场的潜在影响
2. 行业相关性：对特定行业的相关程度
3. 信息新颖度：信息的创新性和独特性
4. 紧急程度：是否需要立即关注

返回格式：{{
    "market_impact": 85,
    "industry_relevance": 70,
    "novelty_score": 60,
    "urgency": 75
}}"""
        
        # 使用V-API模型
        response = await litellm.acompletion(
            model="openai/gpt-4o-mini",  # 使用完整的模型路径
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150,
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            scores = {
                'market_impact': result.get('market_impact', 50),
                'industry_relevance': result.get('industry_relevance', 50),
                'novelty_score': result.get('novelty_score', 50),
                'urgency': result.get('urgency', 50),
            }
        except:
            scores = {
                'market_impact': 50,
                'industry_relevance': 50,
                'novelty_score': 50,
                'urgency': 50,
            }
        
        return {
            'scores': scores,
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens,
        }
    
    async def _extract_keywords(self, content: str, model: str) -> Dict[str, Any]:
        """提取关键词"""
        prompt = f"""请从以下新闻中提取5-10个关键词，返回JSON格式：

{content}

返回格式：{{"keywords": ["关键词1", "关键词2", ...]}}"""
        
        # 使用V-API模型
        response = await litellm.acompletion(
            model="openai/gpt-4o-mini",  # 使用完整的模型路径
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100,
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            keywords = result.get('keywords', [])[:10]
        except:
            keywords = []
        
        return {
            'keywords': keywords,
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens,
        }
    
    async def _analyze_sentiment(self, content: str, model: str) -> Dict[str, Any]:
        """情感分析"""
        prompt = f"""请分析以下新闻的情感倾向，返回JSON格式：

{content}

返回格式：{{"sentiment": "positive/negative/neutral"}}"""
        
        # 使用V-API模型
        response = await litellm.acompletion(
            model="openai/gpt-4o-mini",  # 使用完整的模型路径
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50,
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            sentiment = result.get('sentiment', 'neutral')
        except:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens,
        }
    
    async def brief_analyze_with_vapi(self, title: str, content: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        使用V-API进行简要分析
        
        Args:
            title: 新闻标题
            content: 新闻内容
            model: 使用的V-API模型
            
        Returns:
            简要分析结果
        """
        prompt = f"""请对以下新闻进行简要分析，返回JSON格式：

标题: {title}

内容: {content[:1000]}...

分析要求：
1. 生成简短摘要（50字以内）
2. 提取3-5个关键词
3. 分析情感倾向（positive/negative/neutral）
4. 给出简要分类（1-2个类别）
5. 评估新闻重要性（0-100分）

返回格式：
{{
    "summary": "简短摘要",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "sentiment": "positive/negative/neutral",
    "categories": ["分类1", "分类2"],
    "importance": 85
}}"""
        
        try:
            # 直接使用V-API模型
            response = await litellm.acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300,
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                'summary': result.get('summary', ''),
                'keywords': result.get('keywords', []),
                'sentiment': result.get('sentiment', 'neutral'),
                'categories': result.get('categories', []),
                'importance': result.get('importance', 50),
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens,
                'model_used': model,
            }
        except Exception as e:
            print(f"V-API简要分析失败: {e}")
            return {
                'summary': '',
                'keywords': [],
                'sentiment': 'neutral',
                'categories': [],
                'importance': 50,
                'input_tokens': 0,
                'output_tokens': 0,
                'model_used': model,
                'error': str(e),
            }
    
    async def generate_tags(self, title: str, content: str, model: Optional[str] = None) -> Dict[str, Any]:
        """生成新闻标签"""
        model = model or self.default_model
        if model not in self.AVAILABLE_MODELS:
            model = self.default_model
        
        full_content = f"标题: {title}\n\n内容: {content[:3000]}"
        
        prompt = f"""请为以下新闻生成相关标签（5-15个），返回JSON格式，包含标签和相关性评分：

{full_content}

标签应该涵盖：
1. 主题领域（如：科技、财经、AI等）
2. 具体话题（如：人工智能、股票市场、政策等）
3. 情感倾向（如：正面、负面、中性）
4. 重要性级别（如：热点、突发、深度分析等）

返回格式：{{"tags": {{"标签1": 相关度评分, "标签2": 相关度评分}}}}
相关度评分范围：0-100"""
        
        response = await litellm.acompletion(
            model=self.AVAILABLE_MODELS[model]['model'],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            tags = result.get('tags', {})
        except:
            tags = {}
        
        return {
            'tags': tags,
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens,
        }
    
    async def search_news(self, query: str, news_items: List[Dict[str, Any]], model: Optional[str] = None) -> List[Dict[str, Any]]:
        """基于自然语言查询搜索新闻"""
        model = model or self.default_model
        if model not in self.AVAILABLE_MODELS:
            model = self.default_model
        
        # 构建搜索提示
        news_list = "\n\n".join([
            f"新闻{idx+1}:\n标题: {item.get('title', '')}\n内容: {item.get('content', '')[:500]}"
            for idx, item in enumerate(news_items[:20])  # 限制搜索范围
        ])
        
        prompt = f"""请根据以下查询，对提供的新闻进行相关性排序，返回JSON格式：

查询: {query}

新闻列表:
{news_list}

返回格式：{{"results": [{{"index": 新闻索引, "relevance": 相关度评分, "reason": "相关原因"}}]}}
相关度评分范围：0-100
请按照相关度从高到低排序"""
        
        response = await litellm.acompletion(
            model=self.AVAILABLE_MODELS[model]['model'],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            search_results = result.get('results', [])
            
            # 构建排序后的新闻列表
            ranked_news = []
            for item in search_results:
                idx = item.get('index', 0)
                if 0 <= idx < len(news_items):
                    ranked_news.append({
                        **news_items[idx],
                        'search_relevance': item.get('relevance', 0),
                        'search_reason': item.get('reason', ''),
                    })
            
            return ranked_news
        except Exception as e:
            print(f"搜索失败: {e}")
            return news_items
    
    def _accumulate_cost(self, total: Dict[str, Any], result: Dict[str, Any]):
        """累加成本"""
        total['input_tokens'] += result.get('input_tokens', 0)
        total['output_tokens'] += result.get('output_tokens', 0)
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """计算API调用成本"""
        if model not in self.AVAILABLE_MODELS:
            model = self.default_model
        
        config = self.AVAILABLE_MODELS[model]
        input_cost = (input_tokens / 1000) * config['cost_per_1k_input']
        output_cost = (output_tokens / 1000) * config['cost_per_1k_output']
        total_usd = input_cost + output_cost
        
        # 假设汇率 1 USD = 7.2 CNY
        total_cny = total_usd * 7.2
        
        return {
            'cost_usd': round(total_usd, 6),
            'cost_cny': round(total_cny, 6),
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
        }

# 全局LLM引擎实例
llm_engine = LLMEngine()
