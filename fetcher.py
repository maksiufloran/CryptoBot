from binance.client import Client

class MyFetcher:
    def __init__(self, client: Client):
        """
        Inicjalizuje fetchera z gotowym klientem Binance.
        """
        self.client = client

    def get_price(self, symbol: str) -> float:
        """
        Zwraca aktualną cenę rynkową pary symbol (np. 'BTCUSDT').
        """
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])

    def get_exchange_rate(self) -> float:
        """
        Zwraca kurs USDT/PLN na podstawie par BTCUSDT i BTCPLN.
        """
        btc_usdt = float(self.client.get_symbol_ticker(symbol="BTCUSDT")['price'])
        btc_pln  = float(self.client.get_symbol_ticker(symbol="BTCPLN")['price'])
        return btc_pln / btc_usdt

    # def get_balance(self, asset: str) -> float:
    #     """
    #     Zwraca ilość wolnych jednostek danego aktywa.
    #     """
    #     account = self.client.get_account()
    #     for b in account.get('balances', []):
    #         if b['asset'] == asset:
    #             return float(b['free'])
    #     return 0.0