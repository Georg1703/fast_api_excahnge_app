from pydantic import BaseModel


class ExchangeRateBase(BaseModel):
    from_currency_id: int
    to_currency_id: int
    rate: float


class CurrencyConversionResponse(BaseModel):
    from_currency: str
    to_currency: str
    original_amount: float
    converted_amount: float


class LastUpdateResponse(BaseModel):
    last_update: str
