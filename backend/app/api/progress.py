from fastapi import APIRouter

from app.schemas.progress import ProgressSummary

router = APIRouter()


@router.get("/summary", response_model=ProgressSummary)
def progress_summary() -> ProgressSummary:
    return ProgressSummary(user_id=0, completed_lessons=0, active_level="N5")

