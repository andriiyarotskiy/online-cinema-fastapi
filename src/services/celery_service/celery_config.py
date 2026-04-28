from celery import Celery

# from celery.schedules import crontab

from database.session_postgresql import settings

celery_instance = Celery(
    "online_cinema",
    broker=settings.REDIS_BROKER_URL,
    backend=settings.REDIS_BACKEND_URL,
)

celery_instance.conf.update(
    include=["services.celery_service.tasks.tokens"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "delete-expired-tokens-every-10-min": {
            "task": "services.celery_service.tasks.tokens.delete_expired_tokens",
            "schedule": 3600,
            # "schedule": crontab(hour=21),
        }
    },
)
