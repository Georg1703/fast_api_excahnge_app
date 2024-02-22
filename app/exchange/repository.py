from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select

from .schemas import ExchangeRateBase
from .models import Currency, ExchangeRate


async def get_all_currencies(db_session: AsyncSession) -> List[Tuple[int, str]]:
    query = select(Currency.id, Currency.code)
    result = await db_session.execute(query)
    currencies = result.fetchall()
    return currencies


async def delete_all_exchange_rates(db_session: AsyncSession) -> None:
    await db_session.execute(ExchangeRate.__table__.delete())
    await db_session.commit()


async def save_exchange_rates(
    async_session: async_sessionmaker[AsyncSession],
    exchange_rates: List[ExchangeRateBase],
) -> None:
    """Delete all existing exchange rates and insert new ones"""

    await delete_all_exchange_rates(async_session)

    for exchange_rate in exchange_rates:
        async_session.add(ExchangeRate(**exchange_rate.dict()))
    await async_session.commit()


async def get_one_exchange_rate(
    db_session: AsyncSession, from_currency_id: int = None, to_currency_id: int = None
) -> ExchangeRate:
    if not from_currency_id or not to_currency_id:
        query = select(ExchangeRate).order_by(ExchangeRate.created_at.desc()).limit(1)
    else:
        query = select(ExchangeRate).filter(
            ExchangeRate.from_currency_id == from_currency_id,
            ExchangeRate.to_currency_id == to_currency_id,
        )

    result = await db_session.execute(query)
    return result.scalar_one()


async def get_currency_by_code(db_session: AsyncSession, code: str) -> Currency:
    query = select(Currency).where(Currency.code == code)
    result = await db_session.execute(query)
    return result.scalar_one_or_none()
