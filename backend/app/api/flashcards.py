from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.content import Lesson
from app.models.flashcard import Flashcard
from app.schemas.flashcard import FlashcardResponse, FlashcardSummary

router = APIRouter()


@router.get("/", response_model=list[FlashcardSummary])
def list_flashcard_sets(db: Session = Depends(get_db)) -> list[FlashcardSummary]:
    lessons = db.query(Lesson).order_by(Lesson.code).all()
    summaries: list[FlashcardSummary] = []
    for lesson in lessons:
        count = db.query(Flashcard).filter(Flashcard.lesson_id == lesson.id).count()
        if count:
            summaries.append(FlashcardSummary(lesson_code=lesson.code, card_count=count, status="ready"))
    return summaries


@router.get("/{lesson_code}", response_model=list[FlashcardResponse])
def get_flashcards(lesson_code: str, db: Session = Depends(get_db)) -> list[FlashcardResponse]:
    lesson = db.query(Lesson).filter(Lesson.code == lesson_code).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    cards = db.query(Flashcard).filter(Flashcard.lesson_id == lesson.id).order_by(Flashcard.order_index).all()
    return [
        FlashcardResponse(
            id=card.id,
            lesson_code=lesson.code,
            front=card.front,
            back=card.back,
            card_type=card.card_type,
            order_index=card.order_index,
        )
        for card in cards
    ]
