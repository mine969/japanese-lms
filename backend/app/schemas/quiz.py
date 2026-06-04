from pydantic import BaseModel


class QuizSummary(BaseModel):
    id: int | None = None
    lesson_code: str
    title: str
    status: str
    question_count: int = 0


class QuestionResponse(BaseModel):
    id: int | None = None
    question_type: str
    prompt: str
    choices: dict | None = None
    order_index: int = 0

    model_config = {"from_attributes": True}


class QuizDetail(QuizSummary):
    questions: list[QuestionResponse] = []


class QuizSubmission(BaseModel):
    answers: dict[str, object]


class QuizResult(BaseModel):
    quiz_id: int
    score: float
    correct: int
    total: int
