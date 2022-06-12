from celery import Celery
from config import get_settings

settings = get_settings()

celery = Celery(__name__)
celery.config_from_object({
    'broker_url': settings.REDIS_URI,
    'result_backend': 'db+'+settings.CELERY_DBURI,
    'result_extended': True,
    'task_track_started': True,
    'timezone': 'Europe/Moscow',
    'beat_dburi': settings.CELERY_DBURI,
    'include': ['controllers.parser.mos_ru'],
    'worker_max_tasks_per_child': 100,
})
