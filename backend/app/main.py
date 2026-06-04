from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin_import, auth, dashboard, flashcards, lessons, progress, quizzes
from app.core.config import settings
from app.database.session import Base, SessionLocal, engine
from app.models import *  # noqa: F403
from app.services.content_seed import seed_beta_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_beta_data(db)
        finally:
            db.close()
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def startup() -> None:
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_beta_data(db)
        finally:
            db.close()


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(lessons.router, prefix="/api/v1/lessons", tags=["lessons"])
app.include_router(quizzes.router, prefix="/api/v1/quizzes", tags=["quizzes"])
app.include_router(flashcards.router, prefix="/api/v1/flashcards", tags=["flashcards"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["progress"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(admin_import.router, prefix="/api/v1/admin/import", tags=["admin-import"])
