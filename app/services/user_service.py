# app/services/user_service.py

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import delete, select

from app.core.security import get_password_hash
from app.models.common_model import Genre, Region
from app.models.user_model import Profile, ProfilePositionLink, User
from app.schemas.profile import ProfileUpdate
from app.schemas.user import UserCreate


class UserService:
    async def get_user_by_email(self, db: AsyncSession, email: str) -> User | None:
        """이메일로 사용자를 조회합니다."""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, user_create: UserCreate) -> User:
        """새로운 사용자를 데이터베이스에 생성"""
        # 이메일 중복 확인 로직
        db_user_by_email = await self.get_user_by_email(db, email=user_create.email)
        if db_user_by_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user_data = user_create.model_dump()
        hashed_password = get_password_hash(user_data.pop("password"))
        user_data["password_hash"] = hashed_password
        user_data["login_type"] = "email"
        db_user = User(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    # 프로필 수정 서비스 로직
    async def update_profile(
        self, db: AsyncSession, user: User, profile_update: ProfileUpdate
    ) -> Profile:
        """사용자의 프로필을 생성하거나 수정"""
        # 1. 사용자의 프로필이 없으면 새로 생성
        profile = user.profile
        if not profile:
            profile = Profile(user_id=user.id)
            db.add(profile)
            # 새로운 프로필은 먼저 DB에 저장하여 ID를 부여받음
            await db.commit()
            await db.refresh(profile)

        # 2. Pydantic 모델에서 업데이트할 데이터만 추출
        update_data = profile_update.model_dump(
            exclude_unset=True, exclude={"positions"}
        )

        # 3. 관계 필드(M:N)를 제외한 나머지 필드를 업데이트
        for key, value in update_data.items():
            if key not in ["region_ids", "positions", "genre_ids"]:
                setattr(profile, key, value)

        # 4. 다대다(M:N) 관계 필드를 업데이트
        if "region_ids" in update_data:
            statement = select(Region).where(Region.id.in_(update_data["region_ids"]))
            results = await db.execute(statement)
            profile.regions = results.scalars().all()

        if "genre_ids" in update_data:
            statement = select(Genre).where(Genre.id.in_(update_data["genre_ids"]))
            results = await db.execute(statement)
            profile.genres = results.scalars().all()

        # 딕셔너리가 아닌, 원래의 Pydantic 객체 리스트를 직접 사용
        if profile_update.positions is not None:
            # 기존 연결을 모두 삭제
            delete_statement = delete(ProfilePositionLink).where(
                ProfilePositionLink.profile_id == profile.id
            )
            await db.execute(delete_statement)

            # 새로운 연결을 생성
            new_links = []
            for pos_payload in profile_update.positions:
                link = ProfilePositionLink(
                    profile_id=profile.id,
                    position_id=pos_payload.position_id,
                    experience_level_id=pos_payload.experience_level_id,
                )
                new_links.append(link)
            db.add_all(new_links)

        await db.commit()
        await db.refresh(profile)

        statement = (
            select(Profile)
            .options(
                selectinload(Profile.regions),
                selectinload(Profile.positions),
                selectinload(Profile.genres),
            )
            .where(Profile.id == profile.id)
        )
        result = await db.execute(statement)
        profile_with_relations = result.scalar_one()

        return profile_with_relations

    async def delete_user(self, db: AsyncSession, user: User):
        """사용자 정보를 DB에서 영구적으로 삭제"""
        profile = user.profile
        if profile:
            await db.delete(profile)
        await db.delete(user)
        await db.commit()


# 서비스 객체 생성
user_service = UserService()
