from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime

from app.database import get_db
from app.schemas import (
    UserConfigResponse, UserConfigUpdate,
    CrawlerConfigResponse, CrawlerConfigCreate, CrawlerConfigUpdate
)
from app.services.news_service import ConfigService, CrawlerService
from app.crawler import crawler_manager
from app.tests.crawler.test_crawler_validity import CrawlerValidityTester

router = APIRouter(prefix="/config", tags=["config"])

# ========== 用户配置 ==========

@router.get("/user", response_model=UserConfigResponse)
async def get_user_config(db: Session = Depends(get_db)):
    """获取用户配置"""
    config = ConfigService.get_user_config(db)
    return config.to_dict()

@router.put("/user", response_model=UserConfigResponse)
async def update_user_config(
    config_data: UserConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新用户配置"""
    config = ConfigService.update_user_config(db, "default", config_data.model_dump())
    return config.to_dict()

# ========== 爬虫配置 ==========

@router.get("/crawlers", response_model=List[CrawlerConfigResponse])
async def list_crawler_configs(db: Session = Depends(get_db)):
    """获取所有爬虫配置"""
    configs = CrawlerService.get_all_configs(db)
    return [config.to_dict() for config in configs]

@router.get("/crawlers/{config_id}", response_model=CrawlerConfigResponse)
async def get_crawler_config(config_id: int, db: Session = Depends(get_db)):
    """获取指定爬虫配置"""
    config = CrawlerService.get_config_by_id(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config.to_dict()

@router.post("/crawlers", response_model=CrawlerConfigResponse)
async def create_crawler_config(
    config_data: CrawlerConfigCreate,
    db: Session = Depends(get_db)
):
    """创建爬虫配置"""
    config = CrawlerService.create_config(db, config_data.model_dump())
    return config.to_dict()

@router.put("/crawlers/{config_id}", response_model=CrawlerConfigResponse)
async def update_crawler_config(
    config_id: int,
    config_data: CrawlerConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新爬虫配置"""
    config = CrawlerService.update_config(db, config_id, config_data.model_dump(exclude_unset=True))
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config.to_dict()

@router.delete("/crawlers/{config_id}")
async def delete_crawler_config(config_id: int, db: Session = Depends(get_db)):
    """删除爬虫配置"""
    success = CrawlerService.delete_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="Config not found")
    return {"message": "Config deleted successfully"}

@router.get("/crawlers/types/available")
async def get_available_crawler_types():
    """获取所有可用的爬虫类型"""
    types = crawler_manager.get_available_types()
    return {"types": types}

# ========== 爬虫测试 ==========

@router.post("/crawlers/{config_id}/test")
async def test_crawler_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """测试指定爬虫配置的有效性"""
    config = CrawlerService.get_config_by_id(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    tester = CrawlerValidityTester()
    is_valid, message = tester.test_crawler(config.to_dict())
    
    # 更新配置的有效性状态
    config.is_valid = is_valid
    config.last_test_at = datetime.utcnow()
    config.test_message = message
    db.commit()
    
    return {
        "id": config.id,
        "name": config.name,
        "is_valid": is_valid,
        "message": message,
        "test_time": config.last_test_at.isoformat()
    }

@router.post("/crawlers/test-all")
async def test_all_crawler_configs(
    db: Session = Depends(get_db)
):
    """批量测试所有爬虫配置的有效性"""
    configs = CrawlerService.get_all_configs(db)
    tester = CrawlerValidityTester()
    results = []
    
    for config in configs:
        is_valid, message = tester.test_crawler(config.to_dict())
        
        # 更新配置的有效性状态
        config.is_valid = is_valid
        config.last_test_at = datetime.utcnow()
        config.test_message = message
        
        results.append({
            "id": config.id,
            "name": config.name,
            "is_valid": is_valid,
            "message": message
        })
    
    db.commit()
    
    return {
        "total": len(configs),
        "results": results
    }
