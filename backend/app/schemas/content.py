from pydantic import BaseModel


class LessonSummary(BaseModel):
    id: int | None = None
    code: str
    title: str
    status: str
    estimated_minutes: int | None = None

    model_config = {"from_attributes": True}


class LessonDetail(LessonSummary):
    prerequisites: str | None = None
    summary: str | None = None
    source_path: str | None = None
    processed_path: str | None = None
    learning_objectives: list[str] = []
    progress_checklist: list[str] = []


class CourseSummary(BaseModel):
    code: str
    title: str
    levels: list[str] = []

    model_config = {"from_attributes": True}
