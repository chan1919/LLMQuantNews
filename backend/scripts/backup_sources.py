#!/usr/bin/env python3
"""
备份当前高质量信息源配置
"""
import sys
import json
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import CrawlerConfig

def backup_sources():
    """备份当前活跃的信息源配置"""
    db = SessionLocal()
    
    try:
        # 导出所有活跃源
        active_sources = db.query(CrawlerConfig).filter(
            CrawlerConfig.is_active == True
        ).all()
        
        backup_data = {
            'total': len(active_sources),
            'sources': []
        }
        
        for config in active_sources:
            backup_data['sources'].append({
                'name': config.name,
                'crawler_type': config.crawler_type,
                'source_url': config.source_url,
                'interval_seconds': config.interval_seconds,
                'priority': config.priority,
                'is_valid': config.is_valid
            })
        
        # 保存到文件
        with open('backup_sources.json', 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f'备份完成！')
        print(f'已备份 {len(active_sources)} 个信息源配置到 backup_sources.json')
        
        # 显示备份内容
        print(f'\n备份的信息源列表:')
        for source in backup_data['sources']:
            valid_mark = '✓' if source['is_valid'] else '✗'
            print(f"  {valid_mark} {source['name']}")
        
    except Exception as e:
        print(f'备份失败：{e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    backup_sources()
