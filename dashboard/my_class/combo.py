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
import combo_orders

sys.path.insert(0, r'/usr/local/WB/dashboard')
import Settings

# import dbrools

main_path_data = os.path.expanduser('/usr/local/WB/data/')
warnings.filterwarnings("ignore")

n_rools = {"BTC": {"price": 2, "decimals": 3},
           "ETH": {"price": 2, "decimals": 3},
           "BNB": {"price": 2, "decimals": 2},
           "XRP": {"price": 4, "decimals": 1},
           "LINK": {"price": 3, "decimals": 2},
           "TRX": {"price": 5, "decimals": 0},
           "EOS": {"price": 3, "decimals": 1},
           "FIL": {"price": 3, "decimals": 1},
           "AAVE": {"price": 2, "decimals": 1},
           "DOT": {"price": 3, "decimals": 1},
           "UNI": {"price": 3, "decimals": 0},
           "YFI": {"price": 1, "decimals": 3},
           "SUSHI": {"price": 3, "decimals": 0},
           "BCH": {"price": 2, "decimals": 3},
           "XTZ": {"price": 3, "decimals": 1},
           "LTC": {"price": 2, "decimals": 3},
           "ADA": {"price": 4, "decimals": 0},
           "XLM": {"price": 5, "decimals": 0},
           "SXP": {"price": 4, "decimals": 1},
           "1INCH": {"price": 4, "decimals": 1}}

markets = {'xrpusdt', 'trxusdt', 'bnbusdt', 'linkusdt', 'aaveusdt'}

# markets = {'xrpusdt', 'ltcusdt', 'ethusdt', 'trxusdt', 'eosusdt', 'bnbusdt',
#            'linkusdt', 'filusdt', 'yfiusdt', 'dotusdt', 'sxpusdt', 'uniusdt',
#            'adausdt', 'aaveusdt'}
# markets = {'xrpusdt'}

symbols = ["XRP", "BTC", "ETH",
           "TRX", "EOS", "BNB",
           "LINK", "FIL", "YFI",
           "DOT", "SXP", "UNI",
           "LTC", "ADA", "AAVE"]

data_klines = {"XRPUSDT": [], "BTCUSDT": [], "ETHUSDT": [],
               "TRXUSDT": [], "EOSUSDT": [], "BNBUSDT": [],
               "LINKUSDT": [], "FILUSDT": [], "YFIUSDT": [],
               "DOTUSDT": [], "SXPUSDT": [], "UNIUSDT": [],
               "LTCUSDT": [], "ADAUSDT": [], "AAVEUSDT": []}

data_false = {"XRPUSDT": False, "BTCUSDT": False, "ETHUSDT": False,
              "TRXUSDT": False, "EOSUSDT": False, "BNBUSDT": False,
              "LINKUSDT": False, "FILUSDT": False, "YFIUSDT": False,
              "DOTUSDT": False, "SXPUSDT": False, "UNIUSDT": False,
              "LTCUSDT": False, "ADAUSDT": False, "AAVEUSDT": False}


def bot_sendtext(bot_message):
    bot_token = telega_api_key
    bot_chat_id = telega_api_secret
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + bot_message
    requests.get(send_text)
    return


class SsrmBot:
    def __init__(self):

        self.api_key = api_key
        self.api_secret = api_secret
        self.bclient = Client(api_key=self.api_key, api_secret=self.api_secret)
        self.bot_ping = True

        self.main_data = data_klines
        self.main_data_hour = data_klines
        self.open_orders = data_false
        self.rsi_signal = data_false

        self.trade = 0
        self.my_price = 0

        self.status = False
        # self.min_amount = min_amount * 50
        self.amount = 0

        self.main_direction = None
        self.new_side = None

        self.order = False
        self.order_id = False

        self.order_id_tp = False
        self.order_id_sl = False

        self.my_tp = 0
        self.my_sl = 0

        self.my_Stoch = data_false

        self.binance_websocket_api_manager = None

    def new_data_1_min(self):
        for i in markets:
            print(f"New data {i.upper()} 1 min START:")
            para = self.bclient.get_historical_klines(
                i.upper(),
                Client.KLINE_INTERVAL_1MINUTE,
                "1 day ago UTC")
            self.main_data[i.upper()] = para
            time.sleep(1)

    def new_data_1_hour(self):
        for i in markets:
            print(f"New data {i.upper()} 1 hour START:")
            para = self.bclient.get_historical_klines(
                i.upper(),
                Client.KLINE_INTERVAL_1HOUR,
                "2 days ago UTC")
            del para[-1]
            self.main_data_hour[i.upper()] = para
            self.algorithm_rsi(i.upper())

    def algorithm(self, current_symbol):
        if not self.open_orders[current_symbol]:
            df = pd.DataFrame(self.main_data[current_symbol],
                              columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                       'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            df['close'] = pd.to_numeric(df['close'])
            df["high"] = pd.to_numeric(df["high"])
            df["low"] = pd.to_numeric(df["low"])

            df['rsi'] = ta.RSI(df['close'].values, timeperiod=12)
            df["slowk"], df["slowd"] = ta.STOCH(df['high'].values, df['low'].values, df['close'].values, 14, 3, 0, 3, 0)
            df["macd"], df["line"], df["hist"] = ta.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)

            if df["slowk"].iloc[-1] <= 20 and df["slowd"].iloc[-1] <= 20:
                self.my_Stoch[current_symbol] = 1
            elif df["slowk"].iloc[-1] >= 80 and df["slowd"].iloc[-1] >= 80:
                self.my_Stoch[current_symbol] = 2

            if self.my_Stoch[current_symbol] == 1 and df["slowk"].iloc[-1] >= 80:
                self.my_Stoch[current_symbol] = False
            elif self.my_Stoch[current_symbol] == 2 and df["slowk"].iloc[-1] <= 20:
                self.my_Stoch[current_symbol] = False

            if df["rsi"].iloc[-1] >= 50:
                my_RSI = 1
            else:
                my_RSI = 2

            if self.my_Stoch[current_symbol] == 1 and my_RSI == 1:
                if df["hist"].iloc[-1] > 0 > df["hist"].iloc[-2] and self.rsi_signal[current_symbol] > 70:
                    self.main_direction = my_RSI
                    # self.place_new_order()
            elif self.my_Stoch[current_symbol] == 2 and my_RSI == 2:
                if df["hist"].iloc[-1] < 0 < df["hist"].iloc[-2] and self.rsi_signal[current_symbol] < 30:
                    self.main_direction = my_RSI
                    # self.place_new_order()

    def algorithm_rsi(self, current_symbol):
        data = pd.DataFrame(self.main_data_hour[current_symbol],
                            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                     'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)

        data['close'] = pd.to_numeric(data['close'])
        data["high"] = pd.to_numeric(data["high"])
        data["low"] = pd.to_numeric(data["low"])

        data.reset_index(inplace=True, drop=True)
        data["RSID"] = ta.RSI(data['close'].values, timeperiod=12)
        self.rsi_signal[current_symbol] = data["RSID"].iloc[-1]

    def run(self):
        print(f"NEW FUTURE START")

        # bot_sendtext(f"NEW FUTURE START")
        self.binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com",
                                                                        output_default="dict")
        self.binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h'],
                                                         markets,
                                                         stream_label="UnicornFy",
                                                         output="UnicornFy")

        # self.binance_websocket_api_manager.create_stream('arr', '!userData',
        #                                                  api_key=self.api_key, api_secret=self.api_secret,
        #                                                  output="dict")

        while self.bot_ping:
            if self.status:
                self.status = False
                self.binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h'],
                                                                 markets,
                                                                 stream_label="UnicornFy",
                                                                 output="UnicornFy")

                # self.binance_websocket_api_manager.create_stream('arr', '!userData',
                #                                                  api_key=self.api_key, api_secret=self.api_secret,
                #                                                  output="dict")

                print(f"PARSER RESTART at {datetime.now().strftime('%H:%M:%S')}")
            else:
                try:
                    if self.binance_websocket_api_manager.is_manager_stopping():
                        exit(0)
                        self.status = True
                    stream_buffer = self.binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
                    if stream_buffer is False:
                        time.sleep(0.01)
                    else:
                        if stream_buffer is not None:
                            try:
                                if "e" in stream_buffer:
                                    pass
                                    # if stream_buffer['e'] == 'ACCOUNT_UPDATE':
                                    #     if stream_buffer['a']['P'][0]['s'] == f'{self.symbol}usdt'.upper() and stream_buffer['a']['P'][0]['pa'] == "0":
                                    #         if self.order == 1:
                                    #             if self.trade >= self.my_price:
                                    #                 self.close_tp_order()
                                    #             if self.trade < self.my_price:
                                    #                 self.close_sl_order()
                                    #         elif self.order == 2:
                                    #             if self.trade > self.my_price:
                                    #                 self.close_sl_order()
                                    #             if self.trade <= self.my_price:
                                    #                 self.close_tp_order()
                                else:
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

                                            if self.main_data[stream_buffer["symbol"]][-1][-6] != stream_buffer['kline']['kline_close_time']:
                                                print(stream_buffer["symbol"], "====>>>  new",
                                                      stream_buffer['kline']['kline_close_time'], "==>> old ",
                                                      self.main_data[stream_buffer["symbol"]][-1][-6])

                                                self.main_data[stream_buffer["symbol"]].append(new_row)
                                                del self.main_data[stream_buffer["symbol"]][0]
                                                self.algorithm(stream_buffer["symbol"])

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
                                            if self.main_data_hour[stream_buffer["symbol"]][-1][-6] != stream_buffer['kline']['kline_close_time']:
                                                self.main_data_hour[stream_buffer["symbol"]].append(new_row)
                                                del self.main_data_hour[stream_buffer["symbol"]][0]
                                                self.algorithm_rsi(stream_buffer["symbol"])
                                time.sleep(0.01)
                            except KeyError:
                                print(f"Exception :\n {stream_buffer}")
                                time.sleep(0.5)
                except Exception as exc:
                    self.status = True
                    traceback.print_exc()
                    bot_sendtext(f"NEW FUTURE Exception : \n {exc}")
                    time.sleep(30)


# new_keys = dbrools.my_keys.find_one()

# telega_api_key = new_keys['telega']['key']
# telega_api_secret = new_keys['telega']['secret']
# api_key = new_keys['bin']['key']
# api_secret = new_keys['bin']['secret']

telega_api_key = Settings.TELEGA_KEY
telega_api_secret = Settings.TELEGA_API
api_key = Settings.API_KEY
api_secret = Settings.API_SECRET

new_data = SsrmBot()

new_data.new_data_1_hour()
new_data.new_data_1_min()
time.sleep(1)
new_data.run()
