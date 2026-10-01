import os
import asyncio
from binance import AsyncClient
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

def main():
    client = Client(API_KEY, API_SECRET)

    res = client.get_exchange_info()
    print(client.response.headers)
    tickers = client.get_ticker()
    for i in tickers:
        if i['symbol'] == "AGLDBTC":
            print(i['lastPrice'])


if __name__ == "__main__":
    main()