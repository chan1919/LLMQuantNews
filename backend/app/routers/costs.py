from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import LLMCostResponse, CostSummary
from app.services.news_service import CostService
from app.config import settings

router = APIRouter(prefix="/costs", tags=["costs"])

@router.get("/summary", response_model=CostSummary)
async def get_cost_summary(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """获取使用统计汇总"""
    if not settings.ENABLE_COST_TRACKING:
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "by_model": {}
        }
    
    return CostService.get_cost_summary(db, days)

@router.get("/models/available")
async def get_available_models():
    """获取所有可用的AI模型"""
    from app.llm import llm_engine
    models = llm_engine.get_available_models()
    return {"models": models}
