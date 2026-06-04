from fastapi import APIRouter

from app.schemas.flashcard import FlashcardSummary

router = APIRouter()


@router.get("/", response_model=list[FlashcardSummary])
def list_flashcard_sets() -> list[FlashcardSummary]:
    return [
        FlashcardSummary(lesson_code="N5-M01-L02", card_count=0, status="needs_repair"),
    ]

