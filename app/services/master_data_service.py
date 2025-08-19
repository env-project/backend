# app/services/master_data.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.common_model import (
    ExperienceLevel,
    Genre,
    Orientation,
    Position,
    RecruitmentType,
    Region,
)


async def get_all_master_data(db: AsyncSession):
    regions_result = await db.execute(select(Region))
    regions = regions_result.scalars().all()

    positions_result = await db.execute(select(Position))
    positions = positions_result.scalars().all()

    genres_result = await db.execute(select(Genre))
    genres = genres_result.scalars().all()

    experience_levels_result = await db.execute(select(ExperienceLevel))
    experience_levels = experience_levels_result.scalars().all()

    orientations_result = await db.execute(select(Orientation))
    orientations = orientations_result.scalars().all()

    recruitment_types_result = await db.execute(select(RecruitmentType))
    recruitment_types = recruitment_types_result.scalars().all()

    return {
        "regions": regions,
        "positions": positions,
        "genres": genres,
        "experience_levels": experience_levels,
        "orientations": orientations,
        "recruitment_types": recruitment_types,
    }
