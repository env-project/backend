# app/main.py
from fastapi import FastAPI

from app.api.v1.image_upload_router import image_upload_router
from app.api.v1.master_data_router import master_data_router
from app.api.v1.recruiting_router import recruiting_router
from app.api.v1.endpoints.user_router import user_router

# from app.api.v1.endpoints import user as user_router  # [추가]

app = FastAPI(
    title="Akabi Project API",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Akhabi API"}


# 앞으로 이곳에 각 기능별 라우터를 추가
# 예: app.include_router(user_router, prefix="/api/v1/users")

# 이미지 업로드
app.include_router(
    image_upload_router, prefix="/api/v1/common/uploads/images", tags=["Image Upload"]
)

# 마스터 데이터
app.include_router(
    master_data_router, prefix="/api/v1/common/master-data", tags=["Master Data"]
)

# 타 사용자 북마크 추가/제거
app.include_router(
    master_data_router, prefix="/api/v1/profiles", tags=["User Bookmark"]
)

# 구인글 북마크 추가/제거
app.include_router(
    master_data_router, prefix="/api/v1/recruiting-posts", tags=["Post Bookmark"]
)

# [추가] user_router를 /api/v1/users 경로에 연결합니다.
app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(recruiting_router)
