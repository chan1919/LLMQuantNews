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
    """获取成本汇总"""
    if not settings.ENABLE_COST_TRACKING:
        return {
            "total_cost_usd": 0,
            "total_cost_cny": 0,
            "total_requests": 0,
            "total_tokens": 0,
            "by_model": {},
            "by_day": []
        }
    
    return CostService.get_cost_summary(db, days)

@router.get("/monthly")
async def get_monthly_cost(db: Session = Depends(get_db)):
    """获取当月成本"""
    cost = CostService.get_monthly_cost(db)
    return {"monthly_cost_usd": cost}

@router.get("/budget")
async def get_budget_status(db: Session = Depends(get_db)):
    """获取预算状态"""
    return CostService.check_budget(db)

@router.get("/models/available")
async def get_available_models():
    """获取所有可用的AI模型"""
    from app.llm import llm_engine
    models = llm_engine.get_available_models()
    return {"models": models}
