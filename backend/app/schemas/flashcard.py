from pydantic import BaseModel


class FlashcardSummary(BaseModel):
    id: int | None = None
    lesson_code: str
    card_count: int
    status: str

