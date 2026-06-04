from pydantic import BaseModel


class ProgressSummary(BaseModel):
    user_id: int
    completed_lessons: int
    active_level: str | None = None

