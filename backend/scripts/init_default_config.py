"""
初始化默认用户配置

使用方法:
    cd backend
    python scripts/init_default_config.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import UserConfig, Base

def init_default_config():
    """初始化默认用户配置"""
    print("初始化默认用户配置...")
    
    # 创建表（如果不存在）
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查是否已存在默认配置
        existing = db.query(UserConfig).filter(UserConfig.user_id == "default").first()
        
        if existing:
            print("✓ 默认配置已存在，跳过初始化")
            return
        
        # 创建默认配置
        default_config = UserConfig(
            user_id="default",
            keywords={
                "量化": 10,
                "AI": 8,
                "人工智能": 8,
                "机器学习": 7,
                "深度学习": 7,
                "大模型": 6,
                "区块链": 5,
                "加密货币": 5,
            },
            industries=[
                "人工智能",
                "量化交易",
                "金融科技",
                "区块链",
            ],
            categories=[
                "AI新闻",
                "量化策略",
                "市场动态",
            ],
            excluded_keywords=[
                "广告",
                "推广",
                "招聘",
                "八卦",
            ],
            ai_weight=0.6,
            rule_weight=0.4,
            min_score_threshold=60.0,
            default_llm_model="gpt-4o",
            enable_ai_summary=True,
            enable_ai_classification=True,
            enable_ai_scoring=True,
            push_enabled=True,
            push_channels=["feishu"],
            position_sensitivity=1.0,
            keyword_positions={
                "加息": {"bias": "bearish", "magnitude": 80},
                "降息": {"bias": "bullish", "magnitude": 70},
                "利好": {"bias": "bullish", "magnitude": 60},
                "利空": {"bias": "bearish", "magnitude": 60},
                "突破": {"bias": "bullish", "magnitude": 65},
                "下跌": {"bias": "bearish", "magnitude": 55},
                "上涨": {"bias": "bullish", "magnitude": 55},
                "监管": {"bias": "bearish", "magnitude": 50},
                "创新": {"bias": "bullish", "magnitude": 45},
            },
            dimension_weights={
                "market": 0.3,
                "industry": 0.25,
                "policy": 0.25,
                "tech": 0.2,
            },
            impact_timeframe="medium",
        )
        
        db.add(default_config)
        db.commit()
        
        print("✅ 默认配置创建成功！")
        print("\n配置内容:")
        keywords_count = len(default_config.keywords) if default_config.keywords else 0
        industries_count = len(default_config.industries) if default_config.industries else 0
        positions_count = len(default_config.keyword_positions) if default_config.keyword_positions else 0
        print(f"  - 关键词: {keywords_count} 个")
        print(f"  - 行业: {industries_count} 个")
        print(f"  - 多空关键词配置: {positions_count} 个")
        print(f"  - AI权重: {default_config.ai_weight}")
        print(f"  - 推送阈值: {default_config.min_score_threshold}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 初始化失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_default_config()
