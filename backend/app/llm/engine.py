
import litellm
from typing import Dict, Any, List, Optional
import time
import json
from datetime import datetime

from app.config import settings
from app.models import LLMCost
from app.llm.vapi_service import vapi_service

class LLMEngine:
    """LLM Engine for processing news"""
    
    AVAILABLE_MODELS = {
        'gpt-4o': {'provider': 'openai', 'model': 'gpt-4o', 'cost_per_1k_input': 0.005, 'cost_per_1k_output': 0.015},
        'gpt-4o-mini': {'provider': 'openai', 'model': 'gpt-4o-mini', 'cost_per_1k_input': 0.00015, 'cost_per_1k_output': 0.0006},
        'deepseek-chat': {'provider': 'deepseek', 'model': 'deepseek-chat', 'cost_per_1k_input': 0.00014, 'cost_per_1k_output': 0.00028},
    }
    
    def __init__(self):
        self.default_model = settings.DEFAULT_LLM_MODEL
        self._setup_api_keys()
        self._setup_vapi()
    
    def _setup_vapi(self):
        if settings.VAPI_API_KEY:
            litellm.api_base = f"{settings.VAPI_BASE_URL or 'https://api.vveai.com'}/v1"
            litellm.api_key = settings.VAPI_API_KEY
            print("V-API configured successfully")

    def _setup_api_keys(self):
        if settings.OPENAI_API_KEY:
            litellm.api_key = settings.OPENAI_API_KEY
            print("OpenAI API key configured")
    
    def get_available_models(self):
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
    
    async def get_vapi_models(self, refresh=False):
        vapi_models = await vapi_service.get_chat_models(refresh)
        return [
            {
                'id': model.get('id'),
                'name': model.get('id'),
                'provider': model.get('owned_by', 'vapi'),
                'cost_per_1k_input': 0.0,
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
    ):
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
            full_content = f"Title: {title}\n\nContent: {content[:3000]}"
            
            if 'summarize' in tasks:
                summary_result = await self._summarize(full_content, model)
                results['summary'] = summary_result['text']
                results['tasks_completed'].append('summarize')
                self._accumulate_cost(total_cost, summary_result)
            
            if 'classify' in tasks:
                classify_result = await self._classify(full_content, model)
                results['categories'] = classify_result['categories']
                results['tasks_completed'].append('classify')
                self._accumulate_cost(total_cost, classify_result)
            
            if 'score' in tasks:
                score_result = await self._score(full_content, model)
                results['scores'] = score_result['scores']
                results['position_bias'] = score_result.get('position_bias')
                results['position_magnitude'] = score_result.get('position_magnitude')
                results['brief_impact'] = score_result.get('brief_impact')
                results['tasks_completed'].append('score')
                self._accumulate_cost(total_cost, score_result)
            
            if 'keywords' in tasks:
                keyword_result = await self._extract_keywords(full_content, model)
                results['keywords'] = keyword_result['keywords']
                results['tasks_completed'].append('keywords')
                self._accumulate_cost(total_cost, keyword_result)
            
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
    
    async def _summarize(self, content: str, model: str):
        prompt = "Please generate a concise summary (under 100 words) for the following news:\n\n" + content + "\n\nPlease return only the summary."
        
        print("Using model: gpt-4o-mini")
        print("API Base:", litellm.api_base)
        
        response = await litellm.acompletion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
        )
        
        return {
            'text': response.choices[0].message.content.strip(),
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens,
        }
    
    async def _classify(self, content: str, model: str):
        prompt = """Please classify the following news (multiple choices allowed), return JSON format:

""" + content + """

Categories: ["Finance", "Technology", "AI", "Blockchain", "Policy", "Market", "Company", "International", "Society"]

Return format: {"categories": ["Category1", "Category2"]}"""
        
        print("Using model: gpt-4o-mini")
        print("API Base:", litellm.api_base)
        
        response = await litellm.acompletion(
            model="gpt-4o-mini",
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
    
    async def _score(self, content: str, model: str):
        prompt = """Please evaluate the following news across dimensions (0-100), return JSON format:

""" + content + """

Dimensions:
1. market_impact: Potential impact on financial markets
2. industry_relevance: Relevance to specific industries
3. novelty_score: Innovativeness and uniqueness
4. urgency: Need for immediate attention
5. position_bias: From investment perspective, bullish/bearish/neutral
6. position_magnitude: 0-100, strength of bias
7. importance: Overall importance 0-100
8. brief_impact: One sentence impact description

Return format: {
    "market_impact": 85,
    "industry_relevance": 70,
    "novelty_score": 60,
    "urgency": 75,
    "position_bias": "bullish",
    "position_magnitude": 70,
    "importance": 85,
    "brief_impact": "Positive impact on tech sector"
}"""
        
        print("Using model: gpt-4o-mini")
        print("API Base:", litellm.api_base)
        
        response = await litellm.acompletion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=250,
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            scores = {
                'market_impact': result.get('market_impact', 50),
                'industry_relevance': result.get('industry_relevance', 50),
                'novelty_score': result.get('novelty_score', 50),
                'urgency': result.get('urgency', 50),
            }
            position_bias = result.get('position_bias', 'neutral')
            position_magnitude = result.get('position_magnitude', 0)
            brief_impact = result.get('brief_impact', '')
        except:
            scores = {
                'market_impact': 50,
                'industry_relevance': 50,
                'novelty_score': 50,
                'urgency': 50,
            }
            position_bias = 'neutral'
            position_magnitude = 0
            brief_impact = ''
        
        return {
            'scores': scores,
            'position_bias': position_bias,
            'position_magnitude': position_magnitude,
            'brief_impact': brief_impact,
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens,
        }
    
    async def _extract_keywords(self, content: str, model: str):
        prompt = """Please extract 5-10 keywords from the following news, return JSON format:

""" + content + """

Return format: {"keywords": ["keyword1", "keyword2", ...]}"""
        
        print("Using model: gpt-4o-mini")
        print("API Base:", litellm.api_base)
        
        response = await litellm.acompletion(
            model="gpt-4o-mini",
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
    
    async def _analyze_sentiment(self, content: str, model: str):
        prompt = """Please analyze sentiment of the following news, return JSON format:

""" + content + """

Return format: {"sentiment": "positive/negative/neutral"}"""
        
        print("Using model: gpt-4o-mini")
        print("API Base:", litellm.api_base)
        
        response = await litellm.acompletion(
            model="gpt-4o-mini",
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
    
    async def brief_analyze_with_vapi(self, title: str, content: str, model: str = "gpt-4o-mini"):
        prompt = """Please analyze the following finance/tech news deeply, return JSON format:

Title: """ + title + """

Content: """ + content[:2000] + """...

Requirements:
1. summary (under 100 words)
2. keywords (3-7)
3. sentiment (positive/negative/neutral)
4. categories (1-2 from: Finance, Technology, AI, Blockchain, Policy, Market, Company, International)
5. importance (0-100)
6. position_bias (bullish/bearish/neutral)
7. position_magnitude (0-100)
8. market_impact (0-100)
9. industry_relevance (0-100)
10. novelty_score (0-100)
11. urgency (0-100)

Return format: {
    "summary": "...",
    "keywords": ["..."],
    "sentiment": "...",
    "categories": ["..."],
    "importance": 85,
    "position_bias": "...",
    "position_magnitude": 70,
    "market_impact": 80,
    "industry_relevance": 75,
    "novelty_score": 60,
    "urgency": 65
}"""
        
        try:
            response = await litellm.acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400,
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                'summary': result.get('summary', ''),
                'keywords': result.get('keywords', []),
                'sentiment': result.get('sentiment', 'neutral'),
                'categories': result.get('categories', []),
                'importance': result.get('importance', 50),
                'position_bias': result.get('position_bias', 'neutral'),
                'position_magnitude': result.get('position_magnitude', 0),
                'market_impact': result.get('market_impact', 50),
                'industry_relevance': result.get('industry_relevance', 50),
                'novelty_score': result.get('novelty_score', 50),
                'urgency': result.get('urgency', 50),
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens,
                'model_used': model,
            }
        except Exception as e:
            print("V-API analysis failed:", e)
            return {
                'summary': '',
                'keywords': [],
                'sentiment': 'neutral',
                'categories': [],
                'importance': 50,
                'position_bias': 'neutral',
                'position_magnitude': 0,
                'market_impact': 50,
                'industry_relevance': 50,
                'novelty_score': 50,
                'urgency': 50,
                'input_tokens': 0,
                'output_tokens': 0,
                'model_used': model,
                'error': str(e),
            }
    
    async def generate_tags(self, title: str, content: str, model: Optional[str] = None):
        model = model or self.default_model
        if model not in self.AVAILABLE_MODELS:
            model = self.default_model
        
        full_content = f"Title: {title}\n\nContent: {content[:3000]}"
        
        prompt = """Please generate relevant tags (5-15) for the following news, return JSON format with relevance scores:

""" + full_content + """

Tags should cover:
1. Topic area (Technology, Finance, AI, etc.)
2. Specific topics
3. Sentiment
4. Importance level

Return format: {"tags": {"tag1": score, "tag2": score}}
Score range: 0-100"""
        
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
    
    async def search_news(self, query: str, news_items: List[Dict[str, Any]], model: Optional[str] = None):
        model = model or self.default_model
        if model not in self.AVAILABLE_MODELS:
            model = self.default_model
        
        news_list = "\n\n".join([
            f"News {idx+1}:\nTitle: {item.get('title', '')}\nContent: {item.get('content', '')[:500]}"
            for idx, item in enumerate(news_items[:20])
        ])
        
        prompt = """Please rank the news by relevance to the query, return JSON format:

Query: """ + query + """

News list:
""" + news_list + """

Return format: {"results": [{"index": news_index, "relevance": score, "reason": "..."}]}
Score range: 0-100
Sort by relevance descending"""
        
        response = await litellm.acompletion(
            model=self.AVAILABLE_MODELS[model]['model'],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            search_results = result.get('results', [])
            
            ranked_news = []
            for item in search_results:
                idx = item.get('index', 0)
                if idx >= 0 and idx < len(news_items):
                    ranked_news.append({
                        **news_items[idx],
                        'search_relevance': item.get('relevance', 0),
                        'search_reason': item.get('reason', ''),
                    })
            
            return ranked_news
        except Exception as e:
            print("Search failed:", e)
            return news_items
    
    def _accumulate_cost(self, total: Dict[str, Any], result: Dict[str, Any]):
        total['input_tokens'] += result.get('input_tokens', 0)
        total['output_tokens'] += result.get('output_tokens', 0)
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int):
        if model not in self.AVAILABLE_MODELS:
            model = self.default_model
        
        config = self.AVAILABLE_MODELS[model]
        input_cost = (input_tokens / 1000) * config['cost_per_1k_input']
        output_cost = (output_tokens / 1000) * config['cost_per_1k_output']
        total_usd = input_cost + output_cost
        total_cny = total_usd * 7.2
        
        return {
            'cost_usd': round(total_usd, 6),
            'cost_cny': round(total_cny, 6),
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
        }

llm_engine = LLMEngine()
