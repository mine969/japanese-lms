from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.content import Lesson
from app.models.flashcard import Flashcard
from app.models.progress import Progress
from app.models.quiz import Quiz
from app.models.user import User

router = APIRouter()


@router.get("/")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    lessons = db.query(Lesson).all()
    progress = db.query(Progress).filter(Progress.user_id == current_user.id).all()
    return {
        "active_level": "N5",
        "current_module": "N5-M01",
        "lesson_count": len(lessons),
        "packaged_lessons": sum(1 for lesson in lessons if lesson.status in {"packaged", "complete_source_lesson"}),
        "quiz_count": db.query(Quiz).count(),
        "flashcard_count": db.query(Flashcard).count(),
        "completed_lessons": sum(1 for item in progress if item.status == "completed" and item.quiz_id is None),
        "next_lesson": "N5-M01-L01",
    }
