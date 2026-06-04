from pydantic import BaseModel


class FlashcardSummary(BaseModel):
    id: int | None = None
    lesson_code: str
    card_count: int
    status: str


class FlashcardResponse(BaseModel):
    id: int | None = None
    lesson_code: str
    front: str
    back: str
    card_type: str
    order_index: int

    model_config = {"from_attributes": True}
