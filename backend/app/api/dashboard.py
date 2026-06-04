from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def dashboard() -> dict[str, object]:
    return {
        "active_level": "N5",
        "current_module": "M01",
        "lesson_status": {
            "complete_source": 2,
            "provisional": 1,
            "placeholder": "N5-M01-L04 onward",
        },
    }

