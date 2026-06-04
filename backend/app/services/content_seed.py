import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.auth.passwords import hash_password
from app.models.content import Course, Lesson, Level, Module
from app.models.flashcard import Flashcard
from app.models.quiz import Question, Quiz
from app.models.user import User


LEVELS = ["N5", "N4", "N3", "N2", "N1"]
MODULES = {
    "N5": [
        ("N5-M01", "Foundations & Self-Introduction"),
        ("N5-M02", "Daily Life & Descriptions"),
        ("N5-M03", "Actions, Places & Time"),
        ("N5-M04", "N5 Review & Mock Exam"),
    ],
    "N4": [
        ("N4-M01", "Verb Forms: Potential, Passive, Causative"),
        ("N4-M02", "Conditionals & Complex Sentences"),
        ("N4-M03", "N4 Vocabulary & Kanji Expansion"),
        ("N4-M04", "N4 Review & Mock Exam"),
    ],
    "N3": [
        ("N3-M01", "Intermediate Grammar"),
        ("N3-M02", "Reading Extended Texts & Inference"),
        ("N3-M03", "Listening at Natural Speed"),
        ("N3-M04", "N3 Review & Mock Exam"),
    ],
    "N2": [
        ("N2-M01", "Advanced Grammar & Formal Patterns"),
        ("N2-M02", "Business Japanese & Keigo Foundations"),
        ("N2-M03", "Academic Reading & Newspaper Japanese"),
        ("N2-M04", "N2 Review & Mock Exam"),
    ],
    "N1": [
        ("N1-M01", "N1 Grammar Mastery"),
        ("N1-M02", "Literary & Academic Japanese"),
        ("N1-M03", "Slang, Culture & Native Communication"),
        ("N1-M04", "N1 Review & Mock Exam"),
    ],
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def seed_beta_data(db: Session) -> None:
    course = _get_or_create_course(db)
    module_lookup = _get_or_create_navigation(db, course)
    _seed_admin(db)
    _seed_lessons(db, module_lookup)
    db.commit()


def _get_or_create_course(db: Session) -> Course:
    course = db.query(Course).filter(Course.code == "JLPT").first()
    if course is None:
        course = Course(
            code="JLPT",
            title="JLPT N5 to N1",
            description="Learning path from N5 foundations to N1 fluency.",
        )
        db.add(course)
        db.flush()
    return course


def _get_or_create_navigation(db: Session, course: Course) -> dict[str, Module]:
    module_lookup: dict[str, Module] = {}
    for level_index, level_code in enumerate(LEVELS, start=1):
        level = db.query(Level).filter(Level.course_id == course.id, Level.code == level_code).first()
        if level is None:
            level = Level(course_id=course.id, code=level_code, title=f"JLPT {level_code}", order_index=level_index)
            db.add(level)
            db.flush()
        for module_index, (module_code, module_title) in enumerate(MODULES[level_code], start=1):
            module = db.query(Module).filter(Module.level_id == level.id, Module.code == module_code).first()
            if module is None:
                module = Module(level_id=level.id, code=module_code, title=module_title, order_index=module_index)
                db.add(module)
                db.flush()
            module_lookup[module_code] = module
    return module_lookup


def _seed_admin(db: Session) -> None:
    email = "admin@example.com"
    if db.query(User).filter(User.email == email).first() is None:
        db.add(
            User(
                email=email,
                hashed_password=hash_password("change-me"),
                display_name="Beta Admin",
                role="admin",
            )
        )


def _seed_lessons(db: Session, module_lookup: dict[str, Module]) -> None:
    processed_dir = project_root() / "content" / "processed-lessons"
    for path in sorted(processed_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        module_code = "-".join(payload["code"].split("-")[:2])
        module = module_lookup.get(module_code)
        if module is None:
            continue
        lesson = db.query(Lesson).filter(Lesson.code == payload["code"]).first()
        if lesson is None:
            lesson = Lesson(module_id=module.id, code=payload["code"], title=payload["title"])
            db.add(lesson)
            db.flush()
        lesson.status = payload.get("status", "packaged")
        lesson.estimated_minutes = payload.get("estimated_minutes")
        lesson.prerequisites = payload.get("prerequisites")
        lesson.summary = payload.get("summary")
        lesson.source_path = payload.get("source_path")
        lesson.processed_path = str(path.relative_to(project_root()))
        _seed_quiz(db, lesson)
        _seed_flashcards(db, lesson)


def _seed_quiz(db: Session, lesson: Lesson) -> None:
    quiz_path = project_root() / "quizzes" / "lms-json" / f"{lesson.code}.json"
    if not quiz_path.exists():
        return
    payload = json.loads(quiz_path.read_text(encoding="utf-8"))
    quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson.id).first()
    if quiz is None:
        quiz = Quiz(lesson_id=lesson.id, title=payload.get("title", f"{lesson.code} Quiz"))
        db.add(quiz)
        db.flush()
    quiz.status = payload.get("status", "ready")
    quiz.source = payload.get("source", "source_markdown")
    existing = {question.order_index: question for question in quiz.questions}
    for index, item in enumerate(payload.get("questions", []), start=1):
        question = existing.get(index)
        if question is None:
            question = Question(quiz_id=quiz.id, order_index=index, question_type=item["question_type"], prompt=item["prompt"], answer_key={})
            db.add(question)
        question.question_type = item["question_type"]
        question.prompt = item["prompt"]
        question.choices = item.get("choices")
        question.answer_key = item.get("answer_key", {})


def _seed_flashcards(db: Session, lesson: Lesson) -> None:
    cards_path = project_root() / "flashcards" / "lms-json" / f"{lesson.code}.json"
    if not cards_path.exists():
        return
    payload = json.loads(cards_path.read_text(encoding="utf-8"))
    existing = {
        card.order_index: card
        for card in db.query(Flashcard).filter(Flashcard.lesson_id == lesson.id).all()
    }
    for index, item in enumerate(payload.get("cards", []), start=1):
        card = existing.get(index)
        if card is None:
            card = Flashcard(lesson_id=lesson.id, order_index=index, front=item["front"], back=item["back"])
            db.add(card)
        card.front = item["front"]
        card.back = item["back"]
        card.card_type = item.get("card_type", "vocabulary")
        card.source = payload.get("source", "source_markdown")
