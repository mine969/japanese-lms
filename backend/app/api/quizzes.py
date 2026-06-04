from fastapi import APIRouter

from app.schemas.quiz import QuizSummary

router = APIRouter()


@router.get("/", response_model=list[QuizSummary])
def list_quizzes() -> list[QuizSummary]:
    return [
        QuizSummary(lesson_code="N5-M01-L02", title="Pending repair", status="needs_repair"),
    ]

