from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.content import Lesson
from app.models.progress import Progress
from app.models.user import User
from app.schemas.progress import ProgressResponse, ProgressSummary, ProgressUpdate

router = APIRouter()


@router.get("/summary", response_model=ProgressSummary)
def progress_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressSummary:
    records = db.query(Progress).filter(Progress.user_id == current_user.id).all()
    lesson_records = [record for record in records if record.lesson_id is not None and record.quiz_id is None]
    scores = [record.score for record in records if record.score is not None]
    return ProgressSummary(
        user_id=current_user.id,
        completed_lessons=sum(1 for record in lesson_records if record.status == "completed"),
        started_lessons=sum(1 for record in lesson_records if record.status != "not_started"),
        active_level="N5",
        average_score=round(sum(scores) / len(scores), 2) if scores else None,
    )


@router.put("/lesson", response_model=ProgressResponse)
def update_lesson_progress(
    payload: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    lesson = db.query(Lesson).filter(Lesson.code == payload.lesson_code).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    progress = (
        db.query(Progress)
        .filter(Progress.user_id == current_user.id, Progress.lesson_id == lesson.id, Progress.quiz_id.is_(None))
        .first()
    )
    if progress is None:
        progress = Progress(user_id=current_user.id, lesson_id=lesson.id)
        db.add(progress)
    progress.status = payload.status
    progress.score = payload.score
    db.commit()
    return ProgressResponse(lesson_code=lesson.code, status=progress.status, score=progress.score)
