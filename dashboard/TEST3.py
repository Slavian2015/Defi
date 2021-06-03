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
import argparse

sys.path.insert(0, r'/usr/local/WB/dashboard')
import Orders
import dbrools

main_path_data = os.path.expanduser('/usr/local/WB/data/')
warnings.filterwarnings("ignore")


def bot_sendtext(bot_message):
    bot_token = telega_api_key
    bot_chat_id = telega_api_secret
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + bot_message
    requests.get(send_text)
    return


class SsrmBot:
    def __init__(self, symbol, min_amount, API_KEY, API_SECRET):
        self.symbol = symbol

        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.bclient = Client(api_key=self.api_key, api_secret=self.api_secret)
        self.bot_ping = True

        self.new_period = 2
        self.multiplicator = 11
        self.supertrend_signal = None

        self.main_data = []
        self.main_data_hour = []
        self.my_ask = 0
        self.my_bid = 0

        self.status = False
        self.min_amount = min_amount
        self.amount = 0
        self.wallet = []

        self.order = False
        self.order_status = False
        self.order_id = False
        self.order_time = False
        self.order_price = 0

        self.my_tp = 0
        self.my_sl = 0

        self.my_Stoch = False
        self.my_RSI = False

    def run(self):
        self.binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures",
                                                                        output_default="UnicornFy")
        self.binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h', 'depth5'],
                                                         [f'{self.symbol}usdt'],
                                                         stream_label="UnicornFy",
                                                         output="UnicornFy")
        while self.bot_ping:
            if self.status:
                self.status = False
                self.binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h', 'depth5'],
                                                                 [f'{self.symbol}usdt'],
                                                                 stream_label="UnicornFy",
                                                                 output="UnicornFy")
                print(f"PARSER RESTART at {datetime.now().strftime('%H:%M:%S')}")
            else:
                try:
                    if self.binance_websocket_api_manager.is_manager_stopping():
                        exit(0)
                        self.status = True
                    stream_buffer = self.binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
                    if stream_buffer:

                        print(stream_buffer)
                        try:
                            if stream_buffer['event_type'] == "bookTicker":
                                print(stream_buffer)
                                self.my_ask = float(stream_buffer['asks'][0][0])
                                self.my_bid = float(stream_buffer['bids'][0][0])
                                # print("ASK :", self.my_ask)

                            else:
                                if stream_buffer['event_type'] == "kline":
                                    if stream_buffer['kline']['interval'] == "1m":
                                        if stream_buffer['event_time'] >= stream_buffer['kline']['kline_close_time']:
                                            new_row = [stream_buffer['kline']['kline_start_time'],
                                                       stream_buffer['kline']['open_price'],
                                                       stream_buffer['kline']['high_price'],
                                                       stream_buffer['kline']['low_price'],
                                                       stream_buffer['kline']['close_price'],
                                                       stream_buffer['kline']['base_volume'],
                                                       stream_buffer['kline']['kline_close_time'],
                                                       None, None, None, None, None]
                                            self.main_data.append(new_row)
                                            del self.main_data[0]
                                    elif stream_buffer['kline']['interval'] == "1h":
                                        if stream_buffer['event_time'] >= stream_buffer['kline']['kline_close_time']:
                                            new_row = [stream_buffer['kline']['kline_start_time'],
                                                       stream_buffer['kline']['open_price'],
                                                       stream_buffer['kline']['high_price'],
                                                       stream_buffer['kline']['low_price'],
                                                       stream_buffer['kline']['close_price'],
                                                       stream_buffer['kline']['base_volume'],
                                                       stream_buffer['kline']['kline_close_time'],
                                                       None, None, None, None, None]
                                            self.main_data_hour.append(new_row)
                                            del self.main_data_hour[0]

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
#
#
# new_data = SsrmBot("trx", float(20), api_key, api_secret)
#
# new_data.run()

bot_ping = True
binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures",
                                                           output_default="dict")
binance_websocket_api_manager.create_stream(['kline_1m'],
                                                 ['trxusdt'],
                                                 stream_label="UnicornFy",
                                                 output="UnicornFy")

binance_websocket_api_manager.create_stream(['trade'],
                                            ['trxusdt'],
                                            output="UnicornFy")

while bot_ping:
    stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
    try:
        if binance_websocket_api_manager.is_manager_stopping():
            exit(0)
            bot_ping = False
            print("bot_ping", bot_ping)
        if stream_buffer:
            # print(stream_buffer, "\n===========================================================")

            try:
                if stream_buffer['event_type'] == "trade":
                    my_ask = float(stream_buffer['price'])
                    my_bid = float(stream_buffer['quantity'])
                    # pass
                    print("\n===========================================================\n", "trade\n", my_ask, my_bid)
                else:
                    pass
                    # print("\n===========================================================\n", "kline\n", stream_buffer)
                # print(stream_buffer, "\n===========================================================")
                # time.sleep(2)
            except KeyError:
                print(f"Exception :\n {stream_buffer}")

    except Exception as exc:
        bot_ping = False
        traceback.print_exc()
        time.sleep(5)


# s = {'stream': 'trxusdt@depth5'}
#
# if "depth5" in s['stream']:
#     print("depth5")
# else:
#     print("NO")