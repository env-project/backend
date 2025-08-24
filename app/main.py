# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.comment_router import comment_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.profile import router as profile_router
from app.api.v1.endpoints.user import router as user_router
from app.api.v1.image_upload_router import image_upload_router
from app.api.v1.master_data_router import master_data_router
from app.api.v1.recruiting_router import recruiting_router

app = FastAPI(title="Akabi Project API", version="0.1.0", redirect_slashes=False)

# CORS 설정
origins = [
    "http://localhost:5173",
    "https://localhost:5173",  # 개발 환경 (Vite)
    "https://frontend-ruddy-phi-24.vercel.app",  # 배포 환경 (Vercel)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
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
