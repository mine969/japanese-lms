from fastapi import APIRouter

from app.schemas.content import CourseSummary, LessonSummary

router = APIRouter()


@router.get("/", response_model=list[LessonSummary])
def list_lessons() -> list[LessonSummary]:
    return [
        LessonSummary(code="N5-M01-L01", title="Source lesson imported externally", status="complete_source_lesson"),
        LessonSummary(code="N5-M01-L02", title="Source lesson imported externally", status="needs_lms_repair"),
        LessonSummary(code="N5-M01-L03", title="Provisional source lesson", status="provisional_complete"),
    ]


@router.get("/courses", response_model=list[CourseSummary])
def list_courses() -> list[CourseSummary]:
    return [CourseSummary(code="JLPT", title="JLPT N5 to N1", levels=["N5", "N4", "N3", "N2", "N1"])]

