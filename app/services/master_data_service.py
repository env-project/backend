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
from app.schemas.master_data_schema import OptionOut


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
        "regions": [OptionOut.model_validate(region) for region in regions],
        "positions": [OptionOut.model_validate(position) for position in positions],
        "genres": [OptionOut.model_validate(genre) for genre in genres],
        "experience_levels": [OptionOut.model_validate(el) for el in experience_levels],
        "orientations": [
            OptionOut.model_validate(orientation) for orientation in orientations
        ],
        "recruitment_types": [OptionOut.model_validate(rt) for rt in recruitment_types],
    }
