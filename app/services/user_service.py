# app/services/user_service.py
from sqlmodel import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    async def create_user(self, db: Session, user_create: UserCreate) -> User:
        """새로운 사용자를 데이터베이스에 생성"""
        # 1. UserCreate 스키마를 딕셔너리로 변환
        user_data = user_create.model_dump()

        # 2. 비밀번호를 해싱하여 딕셔너리에 추가
        hashed_password = get_password_hash(user_data.pop("password"))
        user_data["password_hash"] = hashed_password

        # 3. 필수 필드인 login_type을 명시적으로 추가
        user_data["login_type"] = "email"

        # 4. 완성된 데이터로 User 모델 객체를 생성
        db_user = User(**user_data)

        # 5. 데이터베이스 세션에 객체를 추가하고 커밋
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return db_user


# 서비스 객체 생성
user_service = UserService()
