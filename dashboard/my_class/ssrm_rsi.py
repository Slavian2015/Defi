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
    def __init__(self, symbol, min_amount, API_KEY, API_SECRET):
        self.symbol = symbol
        # self.main_symbol = f'{self.symbol}upusdt' if my_direction == "buy" else f'{self.symbol}downusdt'

        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.bclient = Client(api_key=self.api_key, api_secret=self.api_secret)
        self.bot_ping = True

        self.rsi_signal = None

        self.main_data = []
        self.main_data_hour = []
        self.my_ask_up = 0
        self.my_bid_up = 0

        self.my_ask_down = 0
        self.my_bid_down = 0

        self.status = False
        self.min_amount = min_amount
        self.amount_up = 0
        self.amount_down = 0

        self.main_direction = None
        self.new_side = None
        self.wallet = []

        self.order = False
        self.order_id = False
        self.order_price = 0

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

    def place_new_order(self):
        self.new_side = "UP" if self.main_direction == 1 else "DOWN"

        bot_message = f"Added {self.symbol}{self.new_side} , " \
                      f"\n{round(self.amount_up if self.main_direction == 1 else self.amount_down, 2)}, \n{round(float(self.my_ask_up if self.main_direction == 1 else self.my_ask_down), 5)}," \
                      f"\n SL {round(float(self.my_sl), 5)} / TP {round(float(self.my_tp), 5)}"

        bot_sendtext(bot_message)
        print("\n", bot_message)

        self.order = self.main_direction

        reponse = Orders.my_order(client=self.bclient,
                                  symbol=f"{self.symbol.upper()}{self.new_side}USDT",
                                  side=1,
                                  amount=round(self.amount_up if self.main_direction == 1 else self.amount_down, 2))

        if reponse['error']:
            self.bot_ping = False
            logging.info(f"New order Error:\n {reponse}")
            bot_sendtext(f"New order Error:\n {reponse}")
        else:
            self.order_id = reponse['result']['orderId']
            logging.info(f"New order:\n {reponse}")
            dbrools.insert_history_new(data=reponse)
            self.order_price = self.my_bid_up if self.main_direction == 1 else self.my_bid_down
            data = {
                "symbol": f"{self.symbol}{self.new_side}",
                "amount": round(self.amount_up if self.main_direction == 1 else self.amount_down, 2),
                "price": self.my_ask_up if self.main_direction == 1 else self.my_ask_down,
                "direct": 'BUY',
                "result": 0,
                "date": f"{datetime.now().strftime('%d.%m.%Y')}"
            }
            dbrools.insert_history(data=data)
            self.place_tp_order()

    def place_tp_order(self):
        reponse = Orders.my_order(client=self.bclient,
                                  symbol=f"{self.symbol.upper()}{self.new_side}USDT",
                                  side=2,
                                  amount=round(self.amount, 2),
                                  price=self.my_tp)

        if reponse['error']:
            self.bot_ping = False
            logging.info(f"TP order Error:\n {reponse}")
            bot_sendtext(f"TP order Error:\n {reponse}")
        else:
            self.order_id = reponse['result']['orderId']

    def close_tp_order(self):
        bot_message = f"QUIT {self.symbol.upper()}{self.new_side} , \n{round(self.amount, 2)}, \n{round(float(self.my_tp), 5)}, \n TAKE PROFIT ,\n SL {round(float(self.my_sl), 4)} / TP {round(float(self.my_tp), 4)}"
        bot_sendtext(bot_message)
        print("\n", bot_message)
        data = {
            "symbol": f"{self.symbol}{self.new_side}",
            "amount": round(self.amount, 2),
            "price": self.my_tp,
            "direct": 'SELL',
            "result": 2,
            "date": f"{datetime.now().strftime('%d.%m.%Y')}"
        }
        dbrools.insert_history(data=data)
        self.my_Stoch = False
        self.my_RSI = False
        self.order = False

    def close_sl_order(self):
        bot_message = f"QUIT {self.symbol.upper()}{self.new_side} , \n{round(self.amount, 2)}, \n{round(float(self.my_sl), 5)}, \n STOP LOSS ,\n SL {round(float(self.my_sl), 4)} / TP {round(float(self.my_tp), 4)}"
        bot_sendtext(bot_message)
        print("\n", bot_message)

        result = self.bclient.cancel_order(
            symbol=self.main_symbol.upper(),
            orderId=self.order_id)

        print("\n", result)

        data = {
            "symbol": f"{self.symbol}{self.new_side}",
            "amount": round(self.amount, 2),
            "price": self.my_sl,
            "direct": 'SELL',
            "result": 1,
            "date": f"{datetime.now().strftime('%d.%m.%Y')}"
        }
        dbrools.insert_history(data=data)

        reponse = Orders.my_order(client=self.bclient,
                                  symbol=self.main_symbol.upper(),
                                  side=2,
                                  amount=round(self.amount, 2))
        logging.info(f"QUIT order:\n {reponse}")
        dbrools.insert_history_new(data=reponse)

        if reponse['error']:
            self.bot_ping = False
            logging.info(f"New order Error:\n {reponse}")
            bot_sendtext(f"New order Error:\n {reponse}")
        else:
            self.my_Stoch = False
            self.my_RSI = False
            self.order = False

    def algorithm(self):
        if not self.order:
            df = pd.DataFrame(self.main_data,
                              columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                       'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            df['close'] = pd.to_numeric(df['close'])
            df['close'] = pd.to_numeric(df['close'])
            df["high"] = pd.to_numeric(df["high"])
            df["low"] = pd.to_numeric(df["low"])

            df['rsi'] = ta.RSI(df['close'].values, timeperiod=12)
            df["slowk"], df["slowd"] = ta.STOCH(df['high'].values, df['low'].values, df['close'].values, 14, 3, 0, 3, 0)
            df["macd"], df["line"], df["hist"] = ta.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)

            if df["slowk"].iloc[-1] <= 20 and df["slowd"].iloc[-1] <= 20:
                self.my_Stoch = 1
            elif df["slowk"].iloc[-1] >= 80 and df["slowd"].iloc[-1] >= 80:
                self.my_Stoch = 2

            if self.my_Stoch == 1 and df["slowk"].iloc[-1] >= 80:
                self.my_Stoch = False
            elif self.my_Stoch == 2 and df["slowk"].iloc[-1] <= 20:
                self.my_Stoch = False

            if self.my_Stoch:
                if df["rsi"].iloc[-1] >= 50:
                    self.my_RSI = 1
                else:
                    self.my_RSI = 2

            if self.my_Stoch == 1 and self.my_RSI == 1:
                if df["hist"].iloc[-1] > 0 > df["hist"].iloc[-2] and self.rsi_signal > 70:
                    self.wallet.append(self.amount_up)
                    self.my_sl = self.my_bid_up / 1.018
                    self.my_tp = self.my_ask_up * 1.05
                    self.main_direction = self.my_RSI
                    self.place_new_order()
            elif self.my_Stoch == 2 and self.my_RSI == 2:
                if df["hist"].iloc[-1] < 0 < df["hist"].iloc[-2] and self.rsi_signal < 30:
                    self.wallet.append(self.amount_down)
                    self.my_sl = self.my_bid_down / 1.018
                    self.my_tp = self.my_ask_down * 1.05
                    self.main_direction = self.my_RSI
                    self.place_new_order()

    def algorithm_rsi(self):
        data = pd.DataFrame(self.main_data_hour,
                            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                     'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)

        data['close'] = pd.to_numeric(data['close'])
        data["high"] = pd.to_numeric(data["high"])
        data["low"] = pd.to_numeric(data["low"])

        data.reset_index(inplace=True, drop=True)
        data["RSID"] = ta.RSI(data['close'].values, timeperiod=12)
        self.rsi_signal = data["RSID"].iloc[-1]

    def run(self):
        bot_sendtext("SSRM START")
        binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="UnicornFy")
        binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h'],
                                                    [f'{self.symbol}usdt'],
                                                    stream_label="UnicornFy",
                                                    output="UnicornFy")
        binance_websocket_api_manager.create_stream(['depth5'],
                                                    [f'{self.symbol}upusdt', f'{self.symbol}downusdt'],
                                                    stream_label="UnicornFy",
                                                    output="UnicornFy")

        while self.bot_ping:
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
                                if stream_buffer['symbol'] == f'{self.symbol}upusdt'.upper():
                                    self.my_ask_up = float(stream_buffer['asks'][0][0])
                                    self.my_bid_up = float(stream_buffer['bids'][0][0])

                                    if self.order == 1:
                                        if self.my_ask_up > self.my_tp:
                                            self.close_tp_order()
                                            """ проверить по ID и сохранить ордер в БД"""
                                        if self.my_bid_up <= self.my_sl:
                                            """ отменить TP, Проверить и сохранить ордер в БД"""
                                            self.close_sl_order()
                                    else:
                                        self.amount_up = self.min_amount / float(stream_buffer['asks'][0][0])
                                elif stream_buffer['symbol'] == f'{self.symbol}downusdt'.upper():
                                    self.my_ask_down = float(stream_buffer['asks'][0][0])
                                    self.my_bid_down = float(stream_buffer['bids'][0][0])

                                    if self.order == 2:
                                        if self.my_ask_down > self.my_tp:
                                            self.close_tp_order()
                                            """ проверить по ID и сохранить ордер в БД"""
                                        if self.my_bid_down <= self.my_sl:
                                            """ отменить TP, Проверить и сохранить ордер в БД"""
                                            self.close_sl_order()
                                    else:
                                        self.amount_down = self.min_amount / float(stream_buffer['asks'][0][0])

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
                                            self.algorithm_rsi()

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
new_data.algorithm_rsi()
new_data.new_data_1_min()
time.sleep(1)
new_data.run()
