import json
import time, sys, os, requests
import pandas as pd
from binance.client import Client
import traceback
from datetime import datetime
import warnings
from unicorn_fy.unicorn_fy import UnicornFy
from time import strftime
import Orders
import Settings
import dbrools
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager

api_key = Settings.API_KEY
api_secret = Settings.API_SECRET
bclient = Client(api_key=api_key, api_secret=api_secret)


telega_api_key = Settings.TELEGA_KEY
telega_api_secret = Settings.TELEGA_API

sys.path.insert(0, r'/usr/local/WB')
main_path_data = os.path.expanduser('/usr/local/WB/data/')
warnings.filterwarnings("ignore")

# ################################   SHOW ALL ROWS & COLS   ####################################
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

markets = ['ethusdt',
           'bnbusdt',
           'ltcusdt',
           'dotusdt',
           'eosusdt',
           'trxusdt',
           ]

markets2 = ['ethupusdt',
           'bnbupusdt',
           'ltcupusdt',
           'dotupusdt',
           'eosupusdt',
           'trxupusdt',
           ]

mk = markets+markets2
main_data = {}
current_time = 0
status = False


def new_data():
    t1 = time.time()
    print("New data START:")
    for k in markets:
        print(k)
        ETHUSDT = bclient.get_historical_klines(
            str(k.upper()),
            Client.KLINE_INTERVAL_1MINUTE,
            "8 days ago UTC")

        main_data[str(k.upper())] = {}

        for i in ETHUSDT:
            main_data[str(k.upper())][str(i[0])] = str(i[4])

        time.sleep(2)

    t2 = time.time()

    print("New data Fasa 2 :", (t2-t1)/60)

    for k in markets:
        ETHUSDT2 = bclient.get_klines(
            symbol=str(k.upper()),
            interval=Client.KLINE_INTERVAL_1MINUTE,
            limit=4)
        for i in ETHUSDT2:
            main_data[str(k.upper())][str(i[0])] = str(i[4])

        time.sleep(1)

    for k in markets2:
        ETHUSDT2 = bclient.get_klines(
            symbol=str(k.upper()),
            interval=Client.KLINE_INTERVAL_1MINUTE,
            limit=4)

        main_data[str(k.upper())] = {}
        for i in ETHUSDT2:
            main_data[str(k.upper())][str(i[0])] = str(i[4])

        time.sleep(1)
    t3 = time.time()

    print("New data FINISHED :", (t3-t1)/60)


if __name__ == "__main__":
    new_data()

    binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="UnicornFy")
    binance_websocket_api_manager.create_stream(['kline_1m'], mk, stream_label="UnicornFy",
                                                output="UnicornFy")
    while True:
        if status:
            new_data()
            status = False
            binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com",
                                                                       output_default="UnicornFy")
            binance_websocket_api_manager.create_stream(['kline_1m'], mk, stream_label="UnicornFy",
                                                        output="UnicornFy")
            print(f"PARSER RESTART at {datetime.now().strftime('%H:%M:%S')}")

        else:
            try:
                if binance_websocket_api_manager.is_manager_stopping():
                    exit(0)
                    status = True
                stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
                if stream_buffer is False:
                    time.sleep(0.01)
                else:
                    if stream_buffer is not None:
                        try:
                            main_data[stream_buffer['symbol']][stream_buffer['kline']['kline_close_time']] = \
                                stream_buffer['kline']['close_price']
                            time.sleep(0.5)
                        except KeyError:
                            print(f"Exception :\n {stream_buffer}")
                            time.sleep(0.5)

                        now = time.time()

                        for i in markets:
                            if len(main_data[i.upper()]) > 13000:
                                del main_data[i.upper()][str([*main_data[i.upper()]][0])]

                        if now - current_time > 30:
                            current_time = now
                            data = {}
                            for i in markets:
                                data[i.upper()] = {}
                                data[i.upper()].update({'timestamp': [*main_data[i.upper()]],
                                                        'close': [*main_data[i.upper()].values()]})
                            dbrools.update_full_data(data=data)
            except Exception as exc:
                status = True
                traceback.print_exc()
                time.sleep(30)
