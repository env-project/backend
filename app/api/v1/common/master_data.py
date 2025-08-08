from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.master_data import MasterDataResponse, OptionOut
from app.services.master_data import get_all_master_data
from app.core.database import get_async_session  # 비동기 세션 의존성

router = APIRouter(prefix="/api/v1/common", tags=["Common"])

@router.get("/master-data", response_model=MasterDataResponse)
async def read_master_data(db: AsyncSession = Depends(get_async_session)):  # 비동기 방식
    data = await get_all_master_data(db)  # 반드시 await

    return {
        key: [OptionOut(id=item.id, name=item.name) for item in value]
        for key, value in data.items()
    }
