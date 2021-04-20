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


parser = argparse.ArgumentParser()
parser.add_argument('--symbol', help='bnb or link')
parser.add_argument('--side', help='sell or buy')
parser.add_argument('--amount', help='Amount')
args = parser.parse_args()


def bot_sendtext(bot_message):
    bot_token = telega_api_key
    bot_chat_id = telega_api_secret
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + bot_message
    requests.get(send_text)
    return


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
        self.amount = min_amount
        self.main_direction = my_direction

        self.current_order_amount = 0
        self.wallet = []
        self.order = False

        self.my_tp = 0
        self.my_sl = 0

        self.my_Stoch = False
        self.my_RSI = False

    def new_data_1_min(self):
        print("New data 1 min START:")
        para = self.bclient.get_historical_klines(
            f"{self.symbol}usdt".upper(),
            Client.KLINE_INTERVAL_1MINUTE,
            "1 day ago UTC")
        self.main_data = para
        print("================== new_data_1_min")

    def new_data_1_hour(self):
        print("New data 1 hour START:")
        para = self.bclient.get_historical_klines(
            f"{self.symbol}usdt".upper(),
            Client.KLINE_INTERVAL_1HOUR,
            "2 days ago UTC")
        self.main_data_hour = para
        print("================== new_data_1_hour")

    def place_new_order(self, direction):
        if direction == 1:
            print("====UP======\n",
                  self.symbol,
                  self.amount,
                  self.my_ask,
                  self.my_sl,
                  self.my_tp)
            bot_message = f"Added new order UP {self.symbol} , \n{self.amount}, \n{round(float(self.my_ask), 5)},\n SL {round(float(self.my_sl), 5)} / TP {round(float(self.my_tp), 5)}"
            bot_sendtext(bot_message)
            print("\n", bot_message)
            self.order = direction
            reponse = Orders.my_order(client=self.bclient, symbol=f"{self.symbol.upper()}UPUSDT", side=1, amount=self.amount)
            logging.info(f"New order:\n {reponse}")
            dbrools.insert_history_new(data=reponse)

            data = {
                "symbol": f"{self.symbol}UP",
                "amount": self.amount,
                "price": self.my_ask,
                "direct": 'BUY',
                "date": f"{datetime.now().strftime('%d.%m.%Y')}"
            }
            dbrools.insert_history(data=data)

        else:
            print("====DOWN======\n",
                  self.symbol,
                  self.amount,
                  self.my_ask,
                  self.my_sl,
                  self.my_tp)
            bot_message = f"Added new order DOWN {self.symbol} , \n{self.amount}, \n{round(float(self.my_ask), 5)},\n SL {round(float(self.my_sl), 5)} / TP {round(float(self.my_tp), 5)}"
            bot_sendtext(bot_message)
            print("\n", bot_message)
            self.order = direction
            reponse = Orders.my_order(client=self.bclient, symbol=f"{self.symbol.upper()}DOWNUSDT", side=1, amount=self.amount)
            logging.info(f"New order:\n {reponse}")
            dbrools.insert_history_new(data=reponse)

            data = {
                "symbol": f"{self.symbol}DOWN",
                "amount": self.amount,
                "price": self.my_ask,
                "direct": 'BUY',
                "date": f"{datetime.now().strftime('%d.%m.%Y')}"
            }
            dbrools.insert_history(data=data)


    def close_order(self, direction):
        if direction == 1:
            rep = "STOP LOSS" if self.my_bid <= self.my_sl else "TAKE PROFIT"
            bot_message = f"QUIT order UP {self.symbol} , \n{self.current_order_amount * self.my_bid,}, \n{round(float(self.my_bid), 4)},\n {rep} \nSL {round(float(self.my_sl), 4)} / TP {round(float(self.my_tp), 4)}"
            bot_sendtext(bot_message)
            print("\n", bot_message)
            self.order = False
            reponse = Orders.my_order(client=self.bclient, symbol=f"{self.symbol.upper()}UPUSDT", side=2, amount=self.amount)
            logging.info(f"New order:\n {reponse}")
            dbrools.insert_history_new(data=reponse)

            data = {
                "symbol": f"{self.symbol}UP",
                "amount": self.amount,
                "price": self.my_bid,
                "direct": 'SELL',
                "date": f"{datetime.now().strftime('%d.%m.%Y')}"
            }
            dbrools.insert_history(data=data)

        else:
            rep = "STOP LOSS" if self.my_bid >= self.my_sl else "TAKE PROFIT"
            bot_message = f"QUIT order DOWN {self.symbol} , \n{self.current_order_amount * self.my_bid,}, \n{round(float(self.my_bid), 4)},\n {rep} \nSL {round(float(self.my_sl), 4)} / TP {round(float(self.my_tp), 4)}"
            bot_sendtext(bot_message)
            print("\n", bot_message)
            self.order = False
            reponse = Orders.my_order(client=self.bclient, symbol=f"{self.symbol.upper()}DOWNUSDT", side=2, amount=self.amount)
            logging.info(f"New order:\n {reponse}")
            dbrools.insert_history_new(data=reponse)

            data = {
                "symbol": f"{self.symbol}DOWN",
                "amount": self.amount,
                "price": self.my_bid,
                "direct": 'SELL',
                "date": f"{datetime.now().strftime('%d.%m.%Y')}"
            }
            dbrools.insert_history(data=data)

        self.my_Stoch = False
        self.my_RSI = False

    def algorithm(self):
        if not self.order:
            df = pd.DataFrame(self.main_data,
                              columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                       'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            df['close'] = pd.to_numeric(df['close'])
            df['close'] = pd.to_numeric(df['close'])
            df["high"] = pd.to_numeric(df["high"])
            df["low"] = pd.to_numeric(df["low"])

            df['rsi'] = ta.RSI(df['close'].values, timeperiod=12)
            df["slowk"], df["slowd"] = ta.STOCH(df['high'].values, df['low'].values, df['close'].values, 14, 3, 0, 3, 0)
            df["macd"], df["line"], df["hist"] = ta.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)

            if df["slowk"].iloc[-1] < 20 and df["slowd"].iloc[-1] < 20:
                self.my_Stoch = 1
            elif df["slowk"].iloc[-1] > 80 or df["slowd"].iloc[-1] > 80:
                self.my_Stoch = 2

            if self.my_Stoch:
                if df["rsi"].iloc[-1] >= 50:
                    self.my_RSI = 1
                else:
                    self.my_RSI = 2

            if self.main_direction == "buy":
                if self.my_Stoch == 1 and self.my_RSI == 1:
                    if df["hist"].iloc[-1] > 0 > df["hist"].iloc[-2] and self.supertrend_signal == 1:
                        self.wallet.append(self.amount)
                        self.my_sl = df['close'].iloc[-1] / 1.01
                        self.my_tp = df['close'].iloc[-1] * 1.02
                        self.place_new_order(1)
            elif self.main_direction == "sell":
                if self.my_Stoch == 2 and self.my_RSI == 2:
                    if df["hist"].iloc[-1] > 0 > df["hist"].iloc[-2] and self.supertrend_signal == 2:
                        self.wallet.append(self.amount)
                        self.my_sl = df['close'].iloc[-1] * 1.01
                        self.my_tp = df['close'].iloc[-1] / 1.02
                        self.place_new_order(2)

    def algorithm_supertrend(self):
        data = pd.DataFrame(self.main_data_hour,
                          columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                   'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)

        data['close'] = pd.to_numeric(data['close'])
        data["high"] = pd.to_numeric(data["high"])
        data["low"] = pd.to_numeric(data["low"])

        data.reset_index(inplace=True, drop=True)
        data['tr0'] = abs(data["high"] - data["low"])
        data['tr1'] = abs(data["high"] - data["close"].shift(1))
        data['tr2'] = abs(data["low"] - data["close"].shift(1))
        data["TR"] = round(data[['tr0', 'tr1', 'tr2']].max(axis=1), 2)
        data["ATR"] = 0.00
        data['BUB'] = 0.00
        data["BLB"] = 0.00
        data["FUB"] = 0.00
        data["FLB"] = 0.00
        data["ST"] = 0.00

        for i, row in data.iterrows():
            if i == 0:
                data.loc[i, 'ATR'] = 0.00
            else:
                data.loc[i, 'ATR'] = ((data.loc[i - 1, 'ATR'] * self.new_period) + data.loc[i, 'TR']) / 14

        data['BUB'] = round(((data["high"] + data["low"]) / 2) + (self.multiplicator * data["ATR"]), 2)
        data['BLB'] = round(((data["high"] + data["low"]) / 2) - (self.multiplicator * data["ATR"]), 2)

        for i, row in data.iterrows():
            if i == 0:
                data.loc[i, "FUB"] = 0.00
            else:
                if (data.loc[i, "BUB"] < data.loc[i - 1, "FUB"]) | (data.loc[i - 1, "close"] > data.loc[i - 1, "FUB"]):
                    data.loc[i, "FUB"] = data.loc[i, "BUB"]
                else:
                    data.loc[i, "FUB"] = data.loc[i - 1, "FUB"]

        for i, row in data.iterrows():
            if i == 0:
                data.loc[i, "FLB"] = 0.00
            else:
                if (data.loc[i, "BLB"] > data.loc[i - 1, "FLB"]) | (data.loc[i - 1, "close"] < data.loc[i - 1, "FLB"]):
                    data.loc[i, "FLB"] = data.loc[i, "BLB"]
                else:
                    data.loc[i, "FLB"] = data.loc[i - 1, "FLB"]

        for i, row in data.iterrows():
            if i == 0:
                data.loc[i, "ST"] = 0.00
            elif (data.loc[i - 1, "ST"] == data.loc[i - 1, "FUB"]) & (data.loc[i, "close"] <= data.loc[i, "FUB"]):
                data.loc[i, "ST"] = data.loc[i, "FUB"]
            elif (data.loc[i - 1, "ST"] == data.loc[i - 1, "FUB"]) & (data.loc[i, "close"] > data.loc[i, "FUB"]):
                data.loc[i, "ST"] = data.loc[i, "FLB"]
            elif (data.loc[i - 1, "ST"] == data.loc[i - 1, "FLB"]) & (data.loc[i, "close"] >= data.loc[i, "FLB"]):
                data.loc[i, "ST"] = data.loc[i, "FLB"]
            elif (data.loc[i - 1, "ST"] == data.loc[i - 1, "FLB"]) & (data.loc[i, "close"] < data.loc[i, "FLB"]):
                data.loc[i, "ST"] = data.loc[i, "FUB"]

        if data["ST"].iloc[-1] <= data["close"].iloc[-1]:
            self.supertrend_signal = 1
        else:
            self.supertrend_signal = 2

    def run(self):
        bot_sendtext("SSRM START")
        binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="UnicornFy")
        binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h', 'depth5'],
                                                    [f'{self.symbol}usdt'],
                                                    stream_label="UnicornFy",
                                                    output="UnicornFy")

        while True:
            if self.status:
                self.status = False

                binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h', 'depth5'],
                                                            [f'{self.symbol}usdt'],
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
                                self.my_ask = float(stream_buffer['asks'][0][0])
                                self.my_bid = float(stream_buffer['bids'][0][0])

                                if self.order == 1:
                                    if self.my_bid <= self.my_sl:
                                        self.close_order(self.order)
                                    elif self.my_bid >= self.my_tp:
                                        self.close_order(self.order)
                                elif self.order == 2:
                                    if self.my_bid >= self.my_sl:
                                        self.close_order(self.order)
                                    elif self.my_bid <= self.my_tp:
                                        self.close_order(self.order)

                            else:
                                if stream_buffer['event_type'] == "kline":
                                    if stream_buffer['kline']['interval'] == "1m":
                                        if stream_buffer['event_time'] >= stream_buffer['kline']['kline_close_time']:

                                            print("Price :", round(float(stream_buffer['kline']['close_price']), 2), self.my_ask, " | ", self.my_bid)
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
                                            self.algorithm()
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
                                            self.algorithm_supertrend()

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


new_data = SsrmBot(args.symbol, float(args.amount), api_key, api_secret, args.side)

new_data.new_data_1_hour()
new_data.algorithm_supertrend()
new_data.new_data_1_min()
time.sleep(1)
new_data.run()
