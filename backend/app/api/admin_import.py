from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.common import StatusResponse
from app.services.content_seed import seed_beta_data

router = APIRouter()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


@router.get("/status", response_model=StatusResponse)
def import_status() -> StatusResponse:
    source_count = len(list((_project_root() / "content" / "source-lessons").glob("*.md")))
    processed_count = len(list((_project_root() / "content" / "processed-lessons").glob("*.json")))
    return StatusResponse(status="ready", message=f"{source_count} source lessons, {processed_count} packaged lessons.")


@router.post("/seed", response_model=StatusResponse)
def seed_imports(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> StatusResponse:
    seed_beta_data(db)
    return StatusResponse(status="ok", message="Beta course data seeded from packaged JSON assets.")
