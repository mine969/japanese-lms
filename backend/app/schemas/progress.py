from pydantic import BaseModel


class ProgressSummary(BaseModel):
    user_id: int
    completed_lessons: int
    active_level: str | None = None
    started_lessons: int = 0
    average_score: float | None = None


class ProgressUpdate(BaseModel):
    lesson_code: str
    status: str
    score: float | None = None


class ProgressResponse(BaseModel):
    lesson_code: str
    status: str
    score: float | None = None
