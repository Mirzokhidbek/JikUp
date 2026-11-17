from arq import cron
from arq.connections import RedisSettings

from app.core.config import get_settings
from app.workers.tasks import collect_saramin, collect_seed, index_jobs, purge_resumes

COLLECT_HOURS = {0, 6, 12, 18}
PURGE_HOUR = 3


class WorkerSettings:
    functions = [collect_seed, collect_saramin, index_jobs, purge_resumes]
    cron_jobs = [
        cron(collect_saramin, hour=COLLECT_HOURS, minute=0, unique=True),
        cron(purge_resumes, hour=PURGE_HOUR, minute=0, unique=True),
    ]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    job_timeout = 1800
    max_tries = 1
    keep_result = 60
