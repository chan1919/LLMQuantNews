#!/usr/bin/env python3
"""
根据测试结果优化信息源配置 - 停用失效的源
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import CrawlerConfig

# 根据测试结果，这些源已失效
FAILED_SOURCES = [
    "证券时报",
    "中国证券报",
    "第一财经",
    "网易新闻-财经",
    "网易新闻-科技",
    "腾讯新闻-新闻中心",
    "腾讯新闻-财经",
    "腾讯新闻-科技",
    "央视新闻",
    "同花顺-财经快讯",
    "东方财富网-财经要闻",
    "极客公园-最新文章",
    "Reuters-头条新闻",
    "Reuters-财经新闻",
    "Reuters-科技新闻",
    "Bloomberg-头条新闻",
    "Bloomberg-市场新闻",
    "Investing.com-经济日历",
    "新浪财经-财经",
    "新浪财经-科技",
]

def disable_failed_sources():
    """停用失效的源"""
    db = SessionLocal()
    
    try:
        disabled_count = 0
        for source_name in FAILED_SOURCES:
            config = db.query(CrawlerConfig).filter(CrawlerConfig.name == source_name).first()
            if config and config.is_active:
                config.is_active = False
                disabled_count += 1
                print(f"已停用: {source_name}")
        
        db.commit()
        
        # 统计
        total = db.query(CrawlerConfig).count()
        active = db.query(CrawlerConfig).filter(CrawlerConfig.is_active == True).count()
        inactive = total - active
        
        print(f"\n优化完成！")
        print(f"停用了 {disabled_count} 个失效源")
        print(f"当前状态: 活跃 {active} / 停用 {inactive} / 总计 {total}")
        
        # 列出可用的源
        print("\n[当前可用的源]:")
        active_sources = db.query(CrawlerConfig).filter(CrawlerConfig.is_active == True).all()
        for i, config in enumerate(active_sources, 1):
            print(f"{i}. {config.name}")
        
    except Exception as e:
        print(f"操作失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    disable_failed_sources()
