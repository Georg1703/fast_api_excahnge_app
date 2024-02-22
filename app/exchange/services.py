from datetime import datetime, timedelta
from typing import List, Tuple
import itertools
import asyncio

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import get_all_currencies
from .schemas import ExchangeRateBase
from ..exceptions import ExternalAPIException
from ..config import settings


async def get_currencies_combinations(
    db_session: AsyncSession,
) -> List[Tuple[str, str]]:
    currencies = await get_all_currencies(db_session)
    combinations = list(itertools.combinations(currencies, 2))
    combinations += [(b, a) for a, b in combinations]
    return combinations


async def get_exchange_rate(
    session: aiohttp.ClientSession, url: str, from_id: int, to_id: int
) -> ExchangeRateBase:
    async with session.get(url) as resp:
        response = await resp.json()
        rate = float(response["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
        return ExchangeRateBase(
            from_currency_id=from_id, to_currency_id=to_id, rate=rate
        )


async def get_exchange_rates_info(db_session: AsyncSession) -> List[ExchangeRateBase]:
    currencies = await get_currencies_combinations(db_session)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for from_currency, to_currency in currencies:
            from_id, from_code = from_currency
            to_id, to_code = to_currency
            api_url = f"{settings.CURRENCY_API_URL}&from_currency={from_code}&to_currency={to_code}&apikey={settings.API_ACCESS_KEY}"
            tasks.append(
                asyncio.ensure_future(
                    get_exchange_rate(session, api_url, from_id, to_id)
                )
            )

        try:
            exchange_info = await asyncio.gather(*tasks)
            return exchange_info
        except KeyError:
            raise ExternalAPIException("External exchange rate service not available")


def get_hours_number_till_midnight() -> int:
    now = datetime.now()
    midnight = datetime(now.year, now.month, now.day) + timedelta(days=1)
    time_remaining = midnight - now
    return time_remaining.total_seconds() // 3600
