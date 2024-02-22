from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    API_ACCESS_KEY: str
    CURRENCY_API_URL: str = (
        "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
