from pydantic import BaseModel


class QuizSummary(BaseModel):
    id: int | None = None
    lesson_code: str
    title: str
    status: str

