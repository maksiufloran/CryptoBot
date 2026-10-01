import time
from indicator import *
from call import Call
from fetcher import MyFetcher
import datetime
from binance import BinanceAPIException
from binance_client import client

call = Call(client)
myFetcher = MyFetcher(client)
indicator = Indicator(client)

MY_CRYPTO = {"XRPUSDC":0.4, "TURBOUSDC":0.3, "SOLUSDC": 0.3}
CRYPTO_MIN = {"XRPUSDC":5, "TURBOUSDC":1, "SOLUSDC": 5}
crypto_status = {"XRPUSDC": False, "TURBOUSDC": False, "SOLUSDC": False}

while True:
    start = time.time()

    for crypto, fraction in MY_CRYPTO.items():
        df = indicator.get_candles_df(crypto, "1m", 200)
        buy_signal  = indicator.should_buy(df)
        sell_signal = indicator.should_sell(df)

        action = ""  # do logowania

        try:
            # ------ BUY ------
            if buy_signal and not crypto_status[crypto]:
                usdc_balance = float(myFetcher.get_balance("USDC"))
                amount_usdc  = usdc_balance * fraction

                # jeśli za mało USDC, nie kupujemy
                if amount_usdc < CRYPTO_MIN[crypto]:
                    action = f"SKIP BUY (<{CRYPTO_MIN[crypto]} USDC)"
                else:
                    price = float(myFetcher.get_price(crypto))
                    qty   = round(amount_usdc / price, 6)
                    call.testBuy(crypto, qty)

                    crypto_status[crypto] = True
                    action = f"BUY qty={qty} (~{amount_usdc:.2f} USDC)"

            # ----- SELL -----
            elif sell_signal and crypto_status[crypto]:
                # najpierw pobieramy, ile mamy tokenów
                asset = crypto.replace("USDC", "").replace("BTC","")  # uproszczone
                token_balance = float(myFetcher.get_balance(asset))

                if token_balance <= 0:
                    action = "SKIP SELL (brak tokenów)"
                else:
                    call.testSell(crypto, token_balance)
                    crypto_status[crypto] = False
                    action = f"SELL qty={token_balance}"

        except BinanceAPIException as e:
            action = f"ERROR {e.code}:{e.message}"
            # wpisz do tester_negative
            with open("logs/tester_negative.txt", "a") as f:
                f.write(f"{datetime.datetime.now()} {crypto} {action}\n")

        # logujemy każdy przebieg
        with open("logs/tester_positive.txt", "a") as f:
            f.write(f"{datetime.datetime.now()} {crypto} {action}\n")

        with open("logs/tester.txt", "a") as f:
            f.write(f"{datetime.datetime.now()}, {crypto}, {action}\n")

    print("Exec time:", time.time() - start)
    time.sleep(5)
