from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AITaskRequest, AITaskResponse
from app.llm import llm_engine
from app.services.news_service import CostService

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/process", response_model=AITaskResponse)
async def process_with_ai(
    request: AITaskRequest,
    db: Session = Depends(get_db)
):
    """使用AI处理内容"""
    model = request.model or "gpt-4o"
    
    # 执行任务
    result = await llm_engine.process_news(
        title="",
        content=request.content,
        tasks=[t.value for t in request.tasks] if request.tasks else ['summarize'],
        model=model
    )
    
    # 记录成本
    if result.get('cost'):
        cost = result['cost']
        cost_info = llm_engine.calculate_cost(
            model,
            cost.get('input_tokens', 0),
            cost.get('output_tokens', 0)
        )
        
        CostService.record_cost(
            db=db,
            model=model,
            provider="openai",  # 简化处理
            prompt_tokens=cost_info['input_tokens'],
            completion_tokens=cost_info['output_tokens'],
            cost_usd=cost_info['cost_usd'],
            cost_cny=cost_info['cost_cny'],
            request_type='manual_process',
            duration_ms=result.get('processing_time_ms')
        )
    
    return {
        "summary": result.get('summary'),
        "categories": result.get('categories', []),
        "keywords": result.get('keywords', []),
        "sentiment": result.get('sentiment'),
        "scores": result.get('scores', {}),
        "cost": None,
        "processing_time_ms": result.get('processing_time_ms', 0)
    }

@router.get("/models")
async def get_available_models():
    """获取可用的AI模型列表"""
    models = llm_engine.get_available_models()
    return {"models": models}


@router.get("/vapi/models")
async def get_vapi_models(refresh: bool = False):
    """获取V-API支持的模型列表"""
    try:
        models = await llm_engine.get_vapi_models(refresh)
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
