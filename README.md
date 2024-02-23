# Exchange App

## Prerequisites

1. Docker
2. make (not mandatory)

## Instalation

Once this repository is cloned on your local:

1. Go to algebraic_expressions directory.
2. Create .env file with variables that exists in .env_example.
3. Get your own api key from this source: https://www.alphavantage.co/ and save it as API_ACCESS_KEY in .env
4. Run: `make go` to build and start django development server + postgres in containers.
5. You are ready to go, open browser and go to http://localhost:8000/docs, you will se 3 available endpoints:
   - /exchange-rates/sync - update all echange rates, if you call that endpoint more then 25 times it will start to return 502 error with retry-after header due to the external api limitations
   - /exchange-rates/last-update - get last update datetime
   - /exchange-rates/{from_currency}/{to_currency}?amount=2 - get converted amount given current exchange rate
