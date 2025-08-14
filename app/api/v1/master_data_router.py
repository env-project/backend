# app/api/v1/master_data_router.py

# 에러 체크용 import
from fastapi import HTTPException
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.master_data_schema import MasterDataResponse, OptionOut
from app.services.master_data_service import get_all_master_data
from app.core.database import get_async_session  # 비동기 세션 의존성

# 에러 체크용 logger
logger = logging.getLogger(__name__)
master_data_router = APIRouter(prefix="/api/v1/common", tags=["Common"])


@master_data_router.get("/", response_model=MasterDataResponse)
async def read_master_data(
    db: AsyncSession = Depends(get_async_session),
):  # 비동기 방식
    try:
        data = await get_all_master_data(db)  # 반드시 await

        # 데이터가 정상적으로 반환되지 않으면 예외를 발생시킬 수 있음
        if not data:
            raise HTTPException(
                status_code=500, detail="Master data is empty or invalid"
            )

        return {
            key: [OptionOut(id=item.id, name=item.name) for item in value]
            for key, value in data.items()
        }

    except Exception as e:
        logger.error(f"Error in read_master_data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")