from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.schemas import (
    UserConfigResponse, UserConfigUpdate,
    CrawlerConfigResponse, CrawlerConfigCreate, CrawlerConfigUpdate
)
from app.services.news_service import ConfigService, CrawlerService
from app.services.config_analysis import config_analysis_service
from app.crawler import crawler_manager
from app.models import UserConfig
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tests.crawler.test_crawler_validity import CrawlerValidityTester

router = APIRouter(prefix="/config", tags=["config"])

# ========== 请求模型 ==========

class AnalyzeDescriptionRequest(BaseModel):
    description: str
    preview_only: bool = True  # True: 只预览不保存, False: 保存到待确认

class ApplyAIConfigRequest(BaseModel):
    confirmed: bool = True  # 是否确认应用

class BlockSourceRequest(BaseModel):
    source_name: str

class UpdateSourceWeightRequest(BaseModel):
    source_name: str
    weight: float

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

# ========== AI配置分析 ==========

@router.post("/analyze-description")
async def analyze_description(
    request: AnalyzeDescriptionRequest,
    db: Session = Depends(get_db)
):
    """
    分析用户描述并生成配置
    
    - preview_only=True: 只返回AI分析结果，不保存到数据库
    - preview_only=False: 保存到pending_ai_config，等待用户确认
    """
    try:
        # 获取现有配置
        existing_config = ConfigService.get_user_config(db)
        
        # 调用AI分析
        ai_config = await config_analysis_service.analyze_description(
            request.description,
            existing_config.to_dict() if existing_config else None
        )
        
        # 添加描述到配置
        ai_config["description"] = request.description
        
        if not request.preview_only:
            # 保存到待确认配置
            if not existing_config:
                existing_config = ConfigService.get_or_create_user_config(db, "default")
            
            existing_config.user_description = request.description
            existing_config.pending_ai_config = ai_config
            existing_config.analysis_mode = "description"
            db.commit()
        
        return {
            "success": True,
            "config": ai_config,
            "saved": not request.preview_only,
            "message": "AI配置分析完成" if request.preview_only else "已保存到待确认配置，请确认后应用"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.get("/pending-ai-config")
async def get_pending_ai_config(db: Session = Depends(get_db)):
    """获取待确认的AI配置"""
    config = ConfigService.get_user_config(db)
    if not config or not config.pending_ai_config:
        return {
            "has_pending": False,
            "config": None
        }
    
    return {
        "has_pending": True,
        "config": config.pending_ai_config,
        "created_at": config.last_config_analysis_at.isoformat() if config.last_config_analysis_at else None
    }

@router.post("/apply-ai-config")
async def apply_ai_config(
    request: ApplyAIConfigRequest,
    db: Session = Depends(get_db)
):
    """应用AI生成的配置"""
    try:
        config = ConfigService.get_user_config(db)
        if not config:
            raise HTTPException(status_code=404, detail="用户配置不存在")
        
        if not config.pending_ai_config:
            raise HTTPException(status_code=400, detail="没有待应用的AI配置")
        
        # 应用配置
        config = config_analysis_service.apply_ai_config(
            config, 
            config.pending_ai_config, 
            confirmed=request.confirmed
        )
        db.commit()
        
        return {
            "success": True,
            "message": "AI配置已应用" if request.confirmed else "配置已更新",
            "config": config.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"应用配置失败: {str(e)}")

@router.post("/reject-ai-config")
async def reject_ai_config(db: Session = Depends(get_db)):
    """拒绝AI生成的配置"""
    config = ConfigService.get_user_config(db)
    if not config:
        raise HTTPException(status_code=404, detail="用户配置不存在")
    
    config.pending_ai_config = {}
    db.commit()
    
    return {
        "success": True,
        "message": "已拒绝AI配置"
    }

@router.post("/reset-to-default")
async def reset_to_default(db: Session = Depends(get_db)):
    """重置为默认配置"""
    try:
        config = ConfigService.get_user_config(db)
        if not config:
            raise HTTPException(status_code=404, detail="用户配置不存在")
        
        # 保留基本信息，重置AI相关配置
        config.analysis_mode = "keywords"
        config.user_description = None
        config.ai_generated_keywords = {}
        config.ai_generated_filters = {}
        config.ai_generated_sources = []
        config.pending_ai_config = {}
        config.last_config_analysis_at = None
        
        db.commit()
        
        return {
            "success": True,
            "message": "已重置为默认配置",
            "config": config.to_dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置失败: {str(e)}")

# ========== 信息源偏好管理 ==========

@router.get("/preferred-sources")
async def get_preferred_sources(db: Session = Depends(get_db)):
    """获取用户偏好的信息源"""
    config = ConfigService.get_user_config(db)
    if not config:
        return {
            "preferred": {},
            "blocked": [],
            "ai_recommended": []
        }
    
    return {
        "preferred": config.preferred_sources or {},
        "blocked": config.blocked_sources or [],
        "ai_recommended": config.ai_generated_sources or []
    }

@router.post("/preferred-sources/update-weight")
async def update_source_weight(
    request: UpdateSourceWeightRequest,
    db: Session = Depends(get_db)
):
    """更新信息源权重"""
    config = ConfigService.get_user_config(db)
    if not config:
        raise HTTPException(status_code=404, detail="用户配置不存在")
    
    if config.preferred_sources is None:
        config.preferred_sources = {}
    
    config.preferred_sources[request.source_name] = max(0.0, min(2.0, request.weight))
    db.commit()
    
    return {
        "success": True,
        "message": f"已更新 {request.source_name} 的权重为 {request.weight}",
        "preferred_sources": config.preferred_sources
    }

@router.post("/block-source")
async def block_source(
    request: BlockSourceRequest,
    db: Session = Depends(get_db)
):
    """屏蔽信息源"""
    config = ConfigService.get_user_config(db)
    if not config:
        raise HTTPException(status_code=404, detail="用户配置不存在")
    
    if config.blocked_sources is None:
        config.blocked_sources = []
    
    if request.source_name not in config.blocked_sources:
        config.blocked_sources.append(request.source_name)
        db.commit()
    
    return {
        "success": True,
        "message": f"已屏蔽信息源: {request.source_name}",
        "blocked_sources": config.blocked_sources
    }

@router.post("/unblock-source")
async def unblock_source(
    request: BlockSourceRequest,
    db: Session = Depends(get_db)
):
    """取消屏蔽信息源"""
    config = ConfigService.get_user_config(db)
    if not config:
        raise HTTPException(status_code=404, detail="用户配置不存在")
    
    if config.blocked_sources and request.source_name in config.blocked_sources:
        config.blocked_sources.remove(request.source_name)
        db.commit()
    
    return {
        "success": True,
        "message": f"已取消屏蔽信息源: {request.source_name}",
        "blocked_sources": config.blocked_sources
    }

@router.get("/recommended-sources")
async def get_recommended_sources(
    industries: str = "",
    categories: str = "",
    db: Session = Depends(get_db)
):
    """根据行业和分类获取推荐的信息源"""
    industry_list = [i.strip() for i in industries.split(",") if i.strip()]
    category_list = [c.strip() for c in categories.split(",") if c.strip()]
    
    recommended = config_analysis_service.get_recommended_sources(industry_list, category_list)
    
    return {
        "industries": industry_list,
        "categories": category_list,
        "recommended_sources": recommended
    }

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
