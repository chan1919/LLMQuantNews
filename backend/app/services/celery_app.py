from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "llmquant",
    broker="memory://",  # 使用内存消息代理
    backend="memory://",  # 使用内存结果后端
    include=["app.services.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
    # 定时任务配置
    beat_schedule={
        'crawl-all-sources-every-5-minutes': {
            'task': 'app.services.tasks.crawl_all_sources',
            'schedule': 300.0,  # 每5分钟
        },
        'push-high-score-news': {
            'task': 'app.services.tasks.push_high_score_news',
            'schedule': 600.0,  # 每10分钟检查推送
        },
        'cleanup-old-news-daily': {
            'task': 'app.services.tasks.cleanup_old_news',
            'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点清理
        },
    },
)
