from contextlib import asynccontextmanager
from fastapi import FastAPI

from .database import init_db
from .exchange.routes import router as currency_router
from .data.currencies import currencies
from .data.exchange_rates import exchange_rates
from .fixtures import populate_currency_table, populate_exchange_rate_table
from .server import get_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await populate_currency_table(currencies)
    await populate_exchange_rate_table(exchange_rates)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(currency_router, prefix="/exchange-rates", tags=["Exchange rates"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
