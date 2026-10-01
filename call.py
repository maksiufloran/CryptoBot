from binance.enums import *
from binance_client import client
import time
import datetime

class Call:
    def __init__(self, client):
        self.client = client

    def testBuy(self, symbol, quantity):
        print(f"Test buying {quantity} of {symbol}")
        return self.client.create_test_order(
        symbol=symbol,
        side=client.SIDE_BUY,        # Mówimy, że to kupno
        type=client.ORDER_TYPE_MARKET,  # Typ zlecenia (MARKET - natychmiast po aktualnej cenie)
        quantity=quantity
        )
        with open("logs/test.log", "a") as f:
            f.write(f"{datetime.datetime.now()}, BUY,{symbol},{quantity}\n")

    def testSell(self, symbol, quantity):
        print(f"Test selling {quantity} of {symbol}")
        # Można dodać logikę testową tutaj
        with open("logs/test.log", "a") as f:
            f.write(f"{datetime.datetime.now()}, SELL,{symbol},{quantity}\n")

    def buy(self, symbol, quantity):
        try:
            response = self.client.order_market_buy(symbol=symbol, quantity=quantity)
            print(f"Bought {quantity} {symbol}")
            print(f"Responce {response}")

            with open("logs/calls_log.txt", "a") as f:
                f.write(f"{datetime.datetime.now()} BUY {symbol} {quantity} {response}\n")


            return response
        except Exception as e:
            print(f"Error buying: {e}")

    def sell(self, symbol, quantity):
        try:
            response = self.client.order_market_sell(symbol=symbol, quantity=round(quantity, 8))
            print(f"Sold {quantity} {symbol}")

            with open("logs/calls_log.txt", "a") as f:
                f.write(f"{datetime.datetime.now()} SELL {symbol} {quantity} {response}\n")

            return response
        except Exception as e:
            print(f"Error selling: {e}")

    def stopLoss(self, symbol, quantity, current_price, purchase_price, stop_loss_percentage=3):
        stop_loss_trigger = purchase_price * (1 - stop_loss_percentage / 100)
        if current_price <= stop_loss_trigger:
            print(f"Stop loss triggered for {symbol}, selling {quantity} at {current_price}")
            with open("logs/calls_log.txt", "a") as f:
                f.write(
                    f"{datetime.datetime.now()} STOP LOSS {symbol} {quantity} {current_price} {purchase_price} {stop_loss_trigger}")

            return self.sell(symbol, quantity)

        return None
