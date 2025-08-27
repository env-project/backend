# app/schemas/master_data.py

from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.schemas.frozen_config import FROZEN_CONFIG


class OptionOut(BaseModel):
    model_config = FROZEN_CONFIG

    id: UUID
    name: str


class MasterDataResponse(BaseModel):
    model_config = FROZEN_CONFIG

    regions: List[OptionOut]
    positions: List[OptionOut]
    genres: List[OptionOut]
    experience_levels: List[OptionOut]
    orientations: List[OptionOut]
    recruitment_types: List[OptionOut]
