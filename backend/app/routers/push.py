from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.news_service import PushService
from app.schemas import PushTestRequest
from app.models import News

router = APIRouter(prefix="/push", tags=["push"])

@router.post("/test")
async def test_push_channel(
    request: PushTestRequest,
    db: Session = Depends(get_db)
):
    """测试推送渠道"""
    from app.services.news_service import ConfigService
    
    config = ConfigService.get_user_config(db)
    
    if request.channel == "feishu":
        success = await PushService.test_push_channel("feishu", {
            "webhook": config.feishu_webhook,
        })
    elif request.channel == "email":
        success = await PushService.test_push_channel("email", {
            "recipients": config.email_recipients,
        })
    else:
        raise HTTPException(status_code=400, detail="Invalid channel")
    
    if success:
        return {"message": f"{request.channel} connection successful"}
    else:
        raise HTTPException(status_code=400, detail=f"{request.channel} connection failed")

@router.post("/{news_id}")
async def push_news(
    news_id: int,
    channels: list[str] = None,
    db: Session = Depends(get_db)
):
    """手动推送指定新闻"""
    from app.services.news_service import ConfigService
    
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    config = ConfigService.get_user_config(db)
    
    if not channels:
        channels = config.push_channels
    
    result = await PushService.push_news(db, news, channels, config)
    
    return result

@router.get("/channels/available")
async def get_available_channels():
    """获取所有可用推送渠道"""
    from app.push import push_manager
    channels = push_manager.get_available_channels()
    return {"channels": channels}
