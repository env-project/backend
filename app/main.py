# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.v1.common import master_data, image_upload

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


# 이미지를 저장하는 디렉토리 경로를 /static/images로 서빙
app.mount("/static/images", StaticFiles(directory="./uploaded_images"), name="images")

# 라우터 등록
app.include_router(master_data.router)
app.include_router(image_upload.router)
