import secrets
from typing import Annotated, Literal

from arq.connections import ArqRedis
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.core.config import get_settings

COLLECT_TASKS = {"seed": "collect_seed", "saramin": "collect_saramin"}
INDEX_TASK = "index_jobs"


async def require_admin(x_admin_token: Annotated[str | None, Header()] = None) -> None:
    expected = get_settings().admin_token.get_secret_value()
    if not expected:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Admin API is disabled")
    if not x_admin_token or not secrets.compare_digest(x_admin_token.encode(), expected.encode()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid admin token")


def get_arq(request: Request) -> ArqRedis:
    pool: ArqRedis = request.app.state.arq
    return pool


router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.post("/collect", status_code=status.HTTP_202_ACCEPTED)
async def collect(
    source: Literal["seed", "saramin"], arq: Annotated[ArqRedis, Depends(get_arq)]
) -> dict[str, str]:
    job = await arq.enqueue_job(COLLECT_TASKS[source], _job_id=f"collect:{source}")
    if job is None:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Collection for {source} is already queued")
    return {"job_id": job.job_id, "source": source}


@router.post("/index", status_code=status.HTTP_202_ACCEPTED)
async def index(arq: Annotated[ArqRedis, Depends(get_arq)]) -> dict[str, str]:
    job = await arq.enqueue_job(INDEX_TASK, _job_id=INDEX_TASK)
    if job is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Indexing is already queued")
    return {"job_id": job.job_id}
