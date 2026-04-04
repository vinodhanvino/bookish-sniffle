from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.user_auth_service import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


class SignInRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=255)


class SignUpRequest(BaseModel):
    user_name: str = Field(min_length=2, max_length=255)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=255)


@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
def sign_up(payload: SignUpRequest) -> dict:
    try:
        result = create_user(
            user_name=payload.user_name,
            email=payload.email,
            password=payload.password,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/sign-in", status_code=status.HTTP_200_OK)
def sign_in(payload: SignInRequest) -> dict:
    result = authenticate_user(email=payload.email, password=payload.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return result
