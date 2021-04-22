import json
import time, sys, os, requests
import pandas as pd
from binance.client import Client
import traceback
from datetime import datetime
import warnings
import talib as ta
import logging
from unicorn_fy.unicorn_fy import UnicornFy
from time import strftime
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager


sys.path.insert(0, r'/usr/local/WB/dashboard')

import dbrools


main_path_data = os.path.expanduser('/usr/local/WB/data/')
warnings.filterwarnings("ignore")


class SsrmBot:
    def __init__(self, symbol, min_amount, API_KEY, API_SECRET, my_direction):
        self.symbol = symbol
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.bclient = Client(api_key=self.api_key, api_secret=self.api_secret)

        self.new_period = 2
        self.multiplicator = 11
        self.supertrend_signal = None

        self.main_data = []
        self.main_data_hour = []
        self.my_ask = 0
        self.my_bid = 0

        self.status = False
        self.min_amount = float(min_amount)
        self.amount = 0
        self.main_direction = my_direction
        self.wallet = []
        self.order = False

        self.my_tp = 0
        self.my_sl = 0

        self.my_Stoch = False
        self.my_RSI = False

    def run(self):
        binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="UnicornFy")
        binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h', 'depth5'],
                                                    [f'{self.symbol}usdt'],
                                                    stream_label="UnicornFy",
                                                    output="UnicornFy")
        binance_websocket_api_manager.create_stream(['depth5'],
                                                    [f'{self.symbol}upusdt', f'{self.symbol}downusdt'],
                                                    stream_label="UnicornFy",
                                                    output="UnicornFy")

        while True:
            if self.status:
                self.status = False

                binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h', 'depth5'],
                                                            [f'{self.symbol}usdt'],
                                                            stream_label="UnicornFy",
                                                            output="UnicornFy")
                binance_websocket_api_manager.create_stream(['depth5'],
                                                            [f'{self.symbol}upusdt', f'{self.symbol}downusdt'],
                                                            stream_label="UnicornFy",
                                                            output="UnicornFy")

                print(f"PARSER RESTART at {datetime.now().strftime('%H:%M:%S')}")

            else:
                try:
                    if binance_websocket_api_manager.is_manager_stopping():
                        exit(0)
                        self.status = True
                    stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
                    if stream_buffer:
                        try:
                            if stream_buffer['event_type'] == "depth":
                                print("\n\n", stream_buffer)

                                if stream_buffer['symbol'] == f'{self.symbol}usdt':
                                    self.my_ask = float(stream_buffer['asks'][0][0])
                                    self.my_bid = float(stream_buffer['bids'][0][0])

                                elif stream_buffer['symbol'] == f'{self.symbol}upusdt' and self.main_direction == "buy":

                                    self.amount = self.min_amount / float(stream_buffer['asks'][0][0])
                                elif stream_buffer['symbol'] == f'{self.symbol}downusdt' and self.main_direction == "sell":
                                    self.amount = self.min_amount / float(stream_buffer['asks'][0][0])

                            time.sleep(0.2)
                        except KeyError:
                            print(f"Exception :\n {stream_buffer}")
                            time.sleep(0.5)
                    else:
                        time.sleep(0.01)

                except Exception as exc:
                    self.status = True
                    traceback.print_exc()
                    time.sleep(30)


new_keys = dbrools.my_keys.find_one()

telega_api_key = new_keys['telega']['key']
telega_api_secret = new_keys['telega']['secret']
api_key = new_keys['bin']['key']
api_secret = new_keys['bin']['secret']


new_data = SsrmBot('bnb', float(100), api_key, api_secret, 'buy')
new_data.run()
