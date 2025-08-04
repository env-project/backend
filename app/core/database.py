from sqlmodel import create_engine

from app.core.config import settings

# 비동기 드라이버를 사용하지 않는 경우 (단순한 시작)
engine = create_engine(settings.DATABASE_URL, echo=True)

# 앞으로 데이터베이스 세션을 생성하는 함수 등을 여기에 추가
