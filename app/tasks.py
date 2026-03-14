# python-engine/app/tasks.py
import os
from celery import Celery
from .workflow import process_request_sync
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

# keep default queue simple
@celery_app.task(bind=True, max_retries=5, default_retry_delay=5)
def enqueue_request(self, request_id):
    try:
        process_request_sync(request_id)
    except Exception as exc:
        logger.exception("Error processing request %s: %s", request_id, exc)
        # Retry with exponential backoff (handled by Celery)
        try:
            raise self.retry(exc=exc)
        except Exception:
            # celery will re-raise MaxRetriesExceededError after max_retries
            raise