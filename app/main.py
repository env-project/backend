from fastapi import FastAPI
from app.api.v1 import common

app = FastAPI(
    title="Akhabi Project API",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """
    서버가 정상적으로 실행 중인지 확인하기 위한 헬스 체크 엔드포인트입니다.
    """
    return {"status": "ok", "message": "Welcome to the Akhabi API!"}


# 앞으로 이곳에 각 기능별 라우터를 추가
# 예: app.include_router(user_router, prefix="/api/v1/users")
app.include_router(common.router)
# 이미 app/api/v1/common.py에 @router.get 등록되어 있으므로 prefix를 붙이면 경로 오류남(원한다면 제거하세요)