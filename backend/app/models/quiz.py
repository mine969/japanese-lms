from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(60), default="draft")
    source: Mapped[str] = mapped_column(String(120), default="source_markdown")
    questions: Mapped[list["Question"]] = relationship(back_populates="quiz")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    question_type: Mapped[str] = mapped_column(String(60))
    prompt: Mapped[str] = mapped_column(Text)
    choices: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    answer_key: Mapped[dict] = mapped_column(JSON)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    quiz: Mapped[Quiz] = relationship(back_populates="questions")
