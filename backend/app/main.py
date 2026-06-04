from fastapi import FastAPI

from app.api import admin_import, auth, dashboard, flashcards, lessons, progress, quizzes
from app.core.config import settings


app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(lessons.router, prefix="/api/v1/lessons", tags=["lessons"])
app.include_router(quizzes.router, prefix="/api/v1/quizzes", tags=["quizzes"])
app.include_router(flashcards.router, prefix="/api/v1/flashcards", tags=["flashcards"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["progress"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(admin_import.router, prefix="/api/v1/admin/import", tags=["admin-import"])

