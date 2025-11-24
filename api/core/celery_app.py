"""
Celery configuration for Lexicon background tasks.
"""
from celery import Celery
from api.config import settings

# Create Celery app
celery_app = Celery(
    "lexicon",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["api.core.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "check-task-deadlines": {
        "task": "api.core.tasks.check_task_deadlines",
        "schedule": 3600.0,  # Run every hour
    },
}
