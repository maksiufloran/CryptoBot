import pandas as pd
from binance_client import client
from binance.client import Client

# --- parametry strategii ---
EMA_FAST     = 9
EMA_SLOW     = 21
RSI_PERIOD   = 14
RSI_LOWER    = 30
RSI_UPPER    = 70

class Indicator:
    def __init__(self, client):
        self.client = client
        # Flagi RSI
        self.rsi_buy = False   # ustawione, gdy RSI spadło poniżej RSI_LOWER
        self.rsi_sell = False  # ustawione, gdy RSI wzrosło powyżej RSI_UPPER

        self.rsi_under30 = False
        self.rsi_over30 = False
        self.rsi_under70 = False
        self.rsi_over70 = False

    def compute_rsi(self, series: pd.Series) -> pd.Series:
        delta     = series.diff()
        gain      = delta.clip(lower=0)
        loss      = -delta.clip(upper=0)
        avg_gain  = gain.ewm(span=RSI_PERIOD, adjust=False).mean()
        avg_loss  = loss.ewm(span=RSI_PERIOD, adjust=False).mean()
        rs        = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['ema_fast'] = df['close'].ewm(span=EMA_FAST, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=EMA_SLOW, adjust=False).mean()
        df['rsi']      = self.compute_rsi(df['close'])
        return df

    def get_candles_df(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        candles = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(candles, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        return self.calculate_indicators(df)

    def update_rsi_flags(self, rsi_prev: float, rsi_curr: float):
        # oversold -> rsi_buy flag
        if rsi_curr < RSI_LOWER:
            self.rsi_buy = True
        # overbought -> rsi_sell flag
        if rsi_curr > RSI_UPPER:
            self.rsi_sell = True

    def update_rsi_flags2(self, rsi_prev: float, rsi_curr: float):
        if rsi_curr < RSI_LOWER:
            self.rsi_under30 = True

        if rsi_curr > RSI_LOWER:
            self.rsi_over30 = True

        if rsi_curr < RSI_UPPER:
            self.rsi_under70 = True

        if rsi_curr > RSI_UPPER:
            self.rsi_over70 = True

    def sholud_buy2(self, df: pd.DataFrame) -> bool:
        if len(df) < 2:
            return False





    def should_buy(self, df: pd.DataFrame) -> bool:
        if len(df) < 2:
            return False

        prev, curr = -2, -1
        # przecięcie EMA
        cross_up = (
            df['ema_fast'].iloc[prev] < df['ema_slow'].iloc[prev] and
            df['ema_fast'].iloc[curr] > df['ema_slow'].iloc[curr]
        )
        # RSI historyczne
        rsi_prev = df['rsi'].iloc[prev]
        rsi_curr = df['rsi'].iloc[curr]
        # aktualizacja flag
        self.update_rsi_flags(rsi_prev, rsi_curr)
        # warunek na sygnał RSI
        rsi_ok = self.rsi_buy and rsi_curr > RSI_LOWER
        # cena nad EMA_SLOW
        above_trend = df['close'].iloc[curr] > df['ema_slow'].iloc[curr]

        if cross_up and rsi_ok and above_trend:
            # reset flagi po zakupie
            self.rsi_buy = False
            return True
        return False


    def should_sell(self, df: pd.DataFrame) -> bool:
        if len(df) < 2:
            return False

        prev, curr = -2, -1
        cross_down = (
            df['ema_fast'].iloc[prev] > df['ema_slow'].iloc[prev] and
            df['ema_fast'].iloc[curr] < df['ema_slow'].iloc[curr]
        )
        rsi_prev = df['rsi'].iloc[prev]
        rsi_curr = df['rsi'].iloc[curr]
        self.update_rsi_flags(rsi_prev, rsi_curr)
        rsi_ok = self.rsi_sell and rsi_curr < RSI_UPPER
        below_trend = df['close'].iloc[curr] < df['ema_slow'].iloc[curr]

        if cross_down and rsi_ok and below_trend:
            self.rsi_sell = False
            return True
        return False

# --- przykład użycia ---
if __name__ == '__main__':
    strat = Indicator(client)
    df = strat.get_candles_df('BTCUSDT', Client.KLINE_INTERVAL_1HOUR, 200)
    print('Buy?', strat.should_buy(df))
    print('Sell?', strat.should_sell(df))
