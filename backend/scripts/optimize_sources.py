#!/usr/bin/env python3
"""
优化信息源配置 - 保留高质量核心源，停用失效源
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import CrawlerConfig

# 保留的高质量核心源列表
KEEP_SOURCES = [
    # 国内源
    "中国新闻网 - 国内",
    "中国新闻网 - 国际",
    "中国新闻网 - 财经",
    "东方财富网 - 股票资讯",
    "36 氪 - 最新资讯",
    "虎嗅网 - 最新文章",
    "爱范儿 - 最新文章",
    
    # 国际源
    "CNBC-头条新闻",
    "CNBC-市场新闻",
    "BBC News-头条新闻",
    "BBC News-世界新闻",
    "The Guardian-头条新闻",
]

# 需要更新 RSS 地址的源
UPDATE_SOURCES = {
    "Reuters-头条新闻": "https://feeds.reuters.com/Reuters/worldNews",
    "Reuters-财经新闻": "https://feeds.reuters.com/reuters/businessNews",
    "Reuters-科技新闻": "https://feeds.reuters.com/reuters/technologyNews",
}

def optimize_sources():
    """优化信息源配置"""
    db = SessionLocal()
    
    try:
        all_configs = db.query(CrawlerConfig).all()
        
        disabled_count = 0
        updated_count = 0
        kept_count = 0
        
        print("="*80)
        print("优化信息源配置")
        print("="*80)
        
        for config in all_configs:
            # 检查是否在保留列表中
            if config.name in KEEP_SOURCES:
                config.is_active = True
                kept_count += 1
                print(f"[保留] {config.name}")
            
            # 检查是否需要更新 RSS 地址
            elif config.name in UPDATE_SOURCES:
                config.source_url = UPDATE_SOURCES[config.name]
                config.is_active = True
                updated_count += 1
                print(f"[更新] {config.name} -> {UPDATE_SOURCES[config.name]}")
            
            # 其他源停用
            else:
                if config.is_active:
                    config.is_active = False
                    disabled_count += 1
                    print(f"[停用] {config.name}")
        
        db.commit()
        
        # 添加更新后的 Reuters 源（如果不存在）
        for name, url in UPDATE_SOURCES.items():
            existing = db.query(CrawlerConfig).filter(CrawlerConfig.name == name).first()
            if not existing:
                new_config = CrawlerConfig(
                    name=name,
                    crawler_type='rss',
                    source_url=url,
                    interval_seconds=300,
                    priority=5,
                    is_active=True
                )
                db.add(new_config)
                print(f"[新增] {name}")
        
        db.commit()
        
        # 统计结果
        total = db.query(CrawlerConfig).count()
        active = db.query(CrawlerConfig).filter(CrawlerConfig.is_active == True).count()
        inactive = total - active
        
        print("\n" + "="*80)
        print("优化完成！")
        print("="*80)
        print(f"停用源数：{disabled_count}")
        print(f"更新源数：{updated_count}")
        print(f"保留源数：{kept_count}")
        print(f"\n当前状态：活跃 {active} / 停用 {inactive} / 总计 {total}")
        
        # 列出所有活跃源
        print("\n[当前活跃的信息源]:")
        active_sources = db.query(CrawlerConfig).filter(CrawlerConfig.is_active == True).order_by(CrawlerConfig.priority.desc()).all()
        for i, config in enumerate(active_sources, 1):
            print(f"{i}. {config.name} (优先级：{config.priority})")
            print(f"   URL: {config.source_url}")
        
    except Exception as e:
        print(f"操作失败：{e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    optimize_sources()
