#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI分析功能
"""

import asyncio
from app.llm import llm_engine
from datetime import datetime


def test_ai_analysis():
    """测试AI分析"""
    print("开始测试AI分析功能...")
    
    # 测试新闻数据
    test_news = {
        "title": "美联储宣布降息25个基点，市场反应积极",
        "content": "美联储在周三的货币政策会议上宣布降息25个基点，将联邦基金利率目标区间下调至1.5%-1.75%。这是美联储自2019年以来的首次降息。美联储主席鲍威尔在新闻发布会上表示，此次降息是为了应对全球经济增长放缓和贸易不确定性带来的风险，同时通胀仍低于2%的目标水平。市场对此反应积极，道琼斯工业平均指数上涨超过300点，标普500指数和纳斯达克综合指数也均有不同程度的上涨。分析师认为，此次降息可能为美国经济提供一定的刺激，但也反映了美联储对经济前景的担忧。"
    }
    
    print(f"测试新闻标题: {test_news['title']}")
    print(f"测试新闻内容: {test_news['content'][:100]}...")
    
    # 执行AI分析
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        print("\n开始执行AI分析...")
        ai_result = loop.run_until_complete(
            llm_engine.process_news(
                test_news['title'],
                test_news['content']
            )
        )
    finally:
        loop.close()
    
    print("\nAI分析结果:")
    print(f"模型使用: {ai_result.get('model_used')}")
    print(f"完成的任务: {ai_result.get('tasks_completed')}")
    print(f"处理时间: {ai_result.get('processing_time_ms')} 毫秒")
    print(f"成本: {ai_result.get('cost')}")
    
    if 'error' in ai_result:
        print(f"错误: {ai_result['error']}")
    else:
        print("\n分析结果:")
        if 'summary' in ai_result:
            print(f"摘要: {ai_result['summary']}")
        if 'categories' in ai_result:
            print(f"分类: {ai_result['categories']}")
        if 'keywords' in ai_result:
            print(f"关键词: {ai_result['keywords']}")
        if 'sentiment' in ai_result:
            print(f"情感: {ai_result['sentiment']}")
        if 'scores' in ai_result:
            print(f"评分: {ai_result['scores']}")
    
    print("\n测试完成")


if __name__ == "__main__":
    test_ai_analysis()
