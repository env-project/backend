from typing import List
from uuid import UUID

from app.models.base_model import BaseModel

class OptionOut(BaseModel):
    id: UUID
    name: str

class MasterDataResponse(BaseModel):
    regions: List[OptionOut]
    positions: List[OptionOut]
    genres: List[OptionOut]
    experience_levels: List[OptionOut]
    orientations: List[OptionOut]
    recruiting_post_types: List[OptionOut]
    recruitment_types: List[OptionOut]
