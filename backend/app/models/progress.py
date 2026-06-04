from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Progress(Base):
    __tablename__ = "progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lesson_id: Mapped[int | None] = mapped_column(ForeignKey("lessons.id"), nullable=True)
    quiz_id: Mapped[int | None] = mapped_column(ForeignKey("quizzes.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(60), default="not_started")
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

