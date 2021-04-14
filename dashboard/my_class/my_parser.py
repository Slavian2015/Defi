import json
import time, sys, os, requests
import pandas as pd
from binance.client import Client
import traceback
from datetime import datetime
import warnings
from unicorn_fy.unicorn_fy import UnicornFy
from time import strftime
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager

sys.path.insert(0, r'/usr/local/WB/dashboard')
import Settings

main_path_data = os.path.expanduser('/usr/local/WB/data/')
warnings.filterwarnings("ignore")


class NewParser:
    markets = ['ethusdt',
               # 'bnbusdt',
               # 'ltcusdt',
               # 'btcusdt',
               ]

    def __init__(self):
        self.api_key = Settings.API_KEY
        self.api_secret = Settings.API_SECRET
        self.bclient = Client(api_key=self.api_key, api_secret=self.api_secret)
        self.main_data_1m = {}
        self.main_data_5m = {}
        self.main_data_1d = {}
        self.ticks = 'ppp'

    def new_data_1_min(self):
        print("New data 1 min START:")
        for k in self.markets:
            para = self.bclient.get_historical_klines(
                str(k.upper()),
                Client.KLINE_INTERVAL_1MINUTE,
                "2 days ago UTC")
            self.main_data_1m[str(k.upper())] = para
        print("New data FINISHED ")
        return self.main_data_1m

    def new_data_5_min(self):
        print("New data 5 min START:")
        for k in self.markets:
            para = self.bclient.get_historical_klines(
                str(k.upper()),
                Client.KLINE_INTERVAL_5MINUTE,
                "90 days ago UTC")
            self.main_data_5m[str(k.upper())] = self.main_data_1m[str(k.upper())] = para
        print("New data FINISHED ")
        return self.main_data_5m

    def new_data_1_day(self):
        print("New data 1 day START:")
        for k in self.markets:
            para = self.bclient.get_historical_klines(
                str(k.upper()),
                Client.KLINE_INTERVAL_1DAY,
                "2 days ago UTC")
            self.main_data_1d[str(k.upper())] = self.main_data_1m[str(k.upper())] = para
        print("New data FINISHED ")
        return self.main_data_1d


class TickParser:
    symbols = ['ethusdt',
               'bnbusdt',
               'ltcusdt',
               'btcusdt',
               'ethupusdt',
               'bnbupusdt',
               'ltcupusdt',
               'btcupusdt',
               'ethdownusdt',
               'bnbdownusdt',
               'ltcdownusdt',
               'btcdownusdt',
               ]

    def __init__(self):
        self.binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com",
                                                                        output_default="UnicornFy")
        self.binance_websocket_api_manager.create_stream(['depth5'],
                                                         self.symbols,
                                                         stream_label="UnicornFy",
                                                         output="UnicornFy")

dat = NewParser()

print(dat.test)

dat.test = "7777"

print(dat.test)


def get_dataframe():
    rep = dat.new_data_1_min()

    data = pd.DataFrame(rep['ethusdt'.upper()],
                        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

    data.set_index('timestamp', inplace=True)

    print(data.head(5))
