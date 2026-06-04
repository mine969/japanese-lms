from pydantic import BaseModel


class LessonSummary(BaseModel):
    code: str
    title: str
    status: str


class CourseSummary(BaseModel):
    code: str
    title: str
    levels: list[str] = []

