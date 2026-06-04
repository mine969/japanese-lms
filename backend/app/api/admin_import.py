from fastapi import APIRouter

from app.schemas.common import StatusResponse

router = APIRouter()


@router.get("/status", response_model=StatusResponse)
def import_status() -> StatusResponse:
    return StatusResponse(status="ready", message="Import pipeline scaffold is available.")


@router.post("/validate/{lesson_code}", response_model=StatusResponse)
def validate_lesson_import(lesson_code: str) -> StatusResponse:
    return StatusResponse(status="pending", message=f"{lesson_code} validation is not yet connected.")

