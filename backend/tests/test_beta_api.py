import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["AUTO_CREATE_TABLES"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app, startup  # noqa: E402


startup()
client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_seeded_lessons_are_available() -> None:
    response = client.get("/api/v1/lessons/")
    assert response.status_code == 200
    codes = {lesson["code"] for lesson in response.json()}
    assert {"N5-M01-L01", "N5-M01-L02", "N5-M01-L03"}.issubset(codes)


def test_l2_gap_repair_assets_are_available() -> None:
    quiz_response = client.get("/api/v1/quizzes/N5-M01-L02")
    assert quiz_response.status_code == 200
    assert quiz_response.json()["question_count"] >= 10

    flashcard_response = client.get("/api/v1/flashcards/N5-M01-L02")
    assert flashcard_response.status_code == 200
    assert len(flashcard_response.json()) >= 40


def test_auth_and_progress_flow() -> None:
    email = "learner@example.com"
    client.post("/api/v1/auth/register", json={"email": email, "password": "secret123", "display_name": "Learner"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "secret123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == email

    progress = client.put(
        "/api/v1/progress/lesson",
        headers=headers,
        json={"lesson_code": "N5-M01-L01", "status": "completed"},
    )
    assert progress.status_code == 200
    assert progress.json()["status"] == "completed"
