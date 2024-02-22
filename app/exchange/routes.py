from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from .services import get_exchange_rates_info, get_hours_number_till_midnight
from .schemas import CurrencyConversionResponse, LastUpdateResponse
from ..database import get_db
from ..exceptions import ExternalAPIException
from . import repository

router = APIRouter()


@router.post("/sync", status_code=status.HTTP_201_CREATED)
async def synchronize_exchange_rates(db_session: AsyncSession = Depends(get_db)):
    """Synchronize exchange rates from the external API"""

    try:
        exchange_info = await get_exchange_rates_info(db_session)
        await repository.save_exchange_rates(db_session, exchange_info)
    except ExternalAPIException as ex:
        hours = get_hours_number_till_midnight()
        headers = {"Retry-After": f"{hours} hours"}
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(ex),
            headers=headers,
        ) from ex
    except SQLAlchemyError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        ) from ex


@router.get("/last-update", response_model=LastUpdateResponse)
async def get_last_updated(db_session: AsyncSession = Depends(get_db)):
    """Get the last updated time of the exchange rates"""

    exchange_rate = await repository.get_one_exchange_rate(db_session)
    try:
        return LastUpdateResponse(
            last_update=exchange_rate.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )
    except SQLAlchemyError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        ) from ex


@router.get("/{from_currency}/{to_currency}", response_model=CurrencyConversionResponse)
async def get_converted_amount(
    from_currency: str,
    to_currency: str,
    amount: Annotated[int | float, Query(gt=0)],
    db_session: AsyncSession = Depends(get_db),
):
    """Get the converted amount between from currency and to currency"""

    from_currency = await repository.get_currency_by_code(
        db_session, from_currency.upper()
    )
    to_currency = await repository.get_currency_by_code(db_session, to_currency.upper())
    if not from_currency or not to_currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found"
        )

    exchange_rate = await repository.get_one_exchange_rate(
        db_session, from_currency.id, to_currency.id
    )
    if not exchange_rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exchange rate not found"
        )

    return CurrencyConversionResponse(
        from_currency=from_currency.code,
        to_currency=to_currency.code,
        original_amount=amount,
        converted_amount=amount * exchange_rate.rate,
    )
