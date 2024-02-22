from typing import List, Dict, Union
from sqlalchemy import select

from .database import engine
from .exchange.models import Currency, ExchangeRate


async def populate_currency_table(data: List[Dict[str, Union[str, float]]]):
    async with engine.begin() as conn:
        async with engine.begin() as conn:
            query = select(Currency)
            result = await conn.execute(query)
            currencies = result.fetchall()

            if not currencies:
                for item in data:
                    await conn.execute(Currency.__table__.insert().values(**item))


async def populate_exchange_rate_table(data: List[Dict[str, Union[str, float]]]):
    async with engine.begin() as conn:
        async with engine.begin() as conn:
            query = select(ExchangeRate)
            result = await conn.execute(query)
            exchange_rates = result.fetchall()

            if not exchange_rates:
                for item in data:
                    await conn.execute(ExchangeRate.__table__.insert().values(**item))
