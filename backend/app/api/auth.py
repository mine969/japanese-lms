from fastapi import APIRouter

from app.auth.jwt import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    token = create_access_token(subject=payload.email, extra_claims={"role": "learner"})
    return TokenResponse(access_token=token)


@router.get("/me")
def me() -> dict[str, str]:
    return {"status": "placeholder", "message": "Current user endpoint requires JWT integration."}

