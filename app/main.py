from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from app.auth import (
    authenticate_user,
    create_token,
    get_user_by_token,
)


app = FastAPI(
    title="ДЭ 2026 API",
    description="Информационная система для демонстрационного экзамена",
    version="1.0.0",
)


TRANSFER_SIMULATOR_URL = (
    "http://192.168.1.200:4444/TransferSimulator"
)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/")
def root():
    return {
        "message": "ДЭ 2026 API работает"
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/api/config")
def config():
    return {
        "transfer_simulator": TRANSFER_SIMULATOR_URL
    }


@app.post("/api/auth/login")
def login(data: LoginRequest):
    user = authenticate_user(
        data.username,
        data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Вы ввели неверный логин или пароль. "
                   "Пожалуйста проверьте ещё раз введенные данные",
        )

    token = create_token(user.username)

    return {
        "message": "Вы успешно авторизовались",
        "token": token,
        "username": user.username,
        "role": user.role,
    }


@app.get("/api/auth/me")
def get_current_user(
    authorization: str | None = Header(default=None),
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Требуется авторизация",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Неверный формат токена",
        )

    token = authorization[7:]
    user = get_user_by_token(token)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Недействительный токен",
        )

    return {
        "username": user.username,
        "role": user.role,
    }