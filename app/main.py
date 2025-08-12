# app/main.py
from fastapi import FastAPI

from app.api.v1.endpoints import auth as auth_router
from app.api.v1.endpoints import user as user_router
from app.api.v1.recruiting_router import recruiting_router

app = FastAPI(
    title="Akabi Project API",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Akhabi API!"}


# 앞으로 이곳에 각 기능별 라우터를 추가
# 예: app.include_router(user_router, prefix="/api/v1/users")

app.include_router(user_router.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(recruiting_router)
