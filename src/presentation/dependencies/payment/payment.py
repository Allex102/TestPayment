from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.query import async_session
from src.infrastructure.query.repositories.payment import SQLAlchemyPaymentRepository


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_payment_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemyPaymentRepository:
    return SQLAlchemyPaymentRepository(session=session)