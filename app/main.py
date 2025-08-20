# app/main.py
from fastapi import FastAPI

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.profile import router as profile_router
from app.api.v1.endpoints.user import router as user_router
from app.api.v1.image_upload_router import image_upload_router
from app.api.v1.master_data_router import master_data_router
from app.api.v1.recruiting_router import recruiting_router
from app.api.v1.comment_router import comment_router

# from app.api.v1.endpoints import user as user_router  # [추가] < 이게 원본이었습니다

app = FastAPI(
    title="Akabi Project API",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Akhabi API!"}


# 앞으로 이곳에 각 기능별 라우터를 추가
# 예: app.include_router(user_router, prefix="/api/v1/users")

app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(profile_router, prefix="/api/v1/profiles", tags=["Profiles"])
app.include_router(recruiting_router, prefix="/api/v1/recruiting", tags=["Recruiting"])
app.include_router(comment_router, prefix="/api/v1/comments", tags=["Comment"])

# 이미지 업로드
app.include_router(
    image_upload_router, prefix="/api/v1/common/uploads/images", tags=["Image Upload"]
)

# 마스터 데이터
app.include_router(
    master_data_router, prefix="/api/v1/common/master-data", tags=["Master Data"]
)
