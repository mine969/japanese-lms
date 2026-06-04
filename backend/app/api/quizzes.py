from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.content import Lesson
from app.models.progress import Progress
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.quiz import QuestionResponse, QuizDetail, QuizResult, QuizSubmission, QuizSummary

router = APIRouter()


@router.get("/", response_model=list[QuizSummary])
def list_quizzes(db: Session = Depends(get_db)) -> list[QuizSummary]:
    quizzes = db.query(Quiz).join(Lesson).order_by(Lesson.code).all()
    return [
        QuizSummary(
            id=quiz.id,
            lesson_code=quiz_lesson.code,
            title=quiz.title,
            status=quiz.status,
            question_count=len(quiz.questions),
        )
        for quiz in quizzes
        for quiz_lesson in [db.query(Lesson).filter(Lesson.id == quiz.lesson_id).first()]
        if quiz_lesson is not None
    ]


@router.get("/{lesson_code}", response_model=QuizDetail)
def get_quiz(lesson_code: str, db: Session = Depends(get_db)) -> QuizDetail:
    lesson = db.query(Lesson).filter(Lesson.code == lesson_code).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson.id).first()
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    questions = sorted(quiz.questions, key=lambda question: question.order_index)
    return QuizDetail(
        id=quiz.id,
        lesson_code=lesson.code,
        title=quiz.title,
        status=quiz.status,
        question_count=len(questions),
        questions=[QuestionResponse.model_validate(question) for question in questions],
    )


@router.post("/{lesson_code}/submit", response_model=QuizResult)
def submit_quiz(
    lesson_code: str,
    payload: QuizSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizResult:
    lesson = db.query(Lesson).filter(Lesson.code == lesson_code).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson.id).first()
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    total = len(quiz.questions)
    correct = 0
    for question in quiz.questions:
        submitted = str(payload.answers.get(str(question.id), payload.answers.get(str(question.order_index), ""))).strip()
        expected = str(question.answer_key.get("answer", "")).strip()
        if submitted and submitted == expected:
            correct += 1
    score = round((correct / total) * 100, 2) if total else 0.0
    progress = (
        db.query(Progress)
        .filter(Progress.user_id == current_user.id, Progress.lesson_id == lesson.id, Progress.quiz_id == quiz.id)
        .first()
    )
    if progress is None:
        progress = Progress(user_id=current_user.id, lesson_id=lesson.id, quiz_id=quiz.id)
        db.add(progress)
    progress.status = "completed" if score >= 60 else "attempted"
    progress.score = score
    db.commit()
    return QuizResult(quiz_id=quiz.id, score=score, correct=correct, total=total)
