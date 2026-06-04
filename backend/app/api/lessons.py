import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.content import Course, Lesson, Level, Module
from app.schemas.content import CourseSummary, LessonDetail, LessonSummary

router = APIRouter()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


@router.get("/", response_model=list[LessonSummary])
def list_lessons(db: Session = Depends(get_db), level: str | None = None) -> list[Lesson]:
    query = db.query(Lesson).join(Module).join(Level).order_by(Level.order_index, Module.order_index, Lesson.code)
    if level:
        query = query.filter(Level.code == level)
    return query.all()


@router.get("/courses", response_model=list[CourseSummary])
def list_courses(db: Session = Depends(get_db)) -> list[CourseSummary]:
    courses = db.query(Course).all()
    summaries: list[CourseSummary] = []
    for course in courses:
        levels = db.query(Level).filter(Level.course_id == course.id).order_by(Level.order_index).all()
        summaries.append(CourseSummary(code=course.code, title=course.title, levels=[level.code for level in levels]))
    return summaries


@router.get("/{lesson_code}", response_model=LessonDetail)
def get_lesson(lesson_code: str, db: Session = Depends(get_db)) -> LessonDetail:
    lesson = db.query(Lesson).filter(Lesson.code == lesson_code).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    payload: dict[str, object] = {}
    if lesson.processed_path:
        path = _project_root() / lesson.processed_path
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
    return LessonDetail(
        id=lesson.id,
        code=lesson.code,
        title=lesson.title,
        status=lesson.status,
        estimated_minutes=lesson.estimated_minutes,
        prerequisites=lesson.prerequisites,
        summary=lesson.summary,
        source_path=lesson.source_path,
        processed_path=lesson.processed_path,
        learning_objectives=list(payload.get("learning_objectives", [])),
        progress_checklist=list(payload.get("progress_checklist", [])),
    )
