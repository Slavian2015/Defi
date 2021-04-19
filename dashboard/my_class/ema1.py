import json
import time, sys, os, requests
import pandas as pd
from binance.client import Client
import traceback
from datetime import datetime
import warnings
import talib as ta
from unicorn_fy.unicorn_fy import UnicornFy
from time import strftime
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager

sys.path.insert(0, r'/usr/local/WB/dashboard')
import Settings

main_path_data = os.path.expanduser('/usr/local/WB/data/')
warnings.filterwarnings("ignore")

telega_api_key = Settings.TELEGA_KEY
telega_api_secret = Settings.TELEGA_API


def bot_sendtext(bot_message):
    bot_token = telega_api_key
    bot_chat_id = telega_api_secret
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + bot_message
    requests.get(send_text)
    return


class EmaBot:
    def __init__(self, symbol, min_amount, API_KEY, API_SECRET):
        self.symbol = symbol
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.bclient = Client(api_key=self.api_key, api_secret=self.api_secret)

        self.main_data = []
        self.my_ask_up = 0
        self.my_bid_up = 0
        self.my_ask_down = 0
        self.my_bid_down = 0

        self.status = False
        self.amount = min_amount

        self.current_order_amount = 0

        self.wallet = []

        self.order = False

        self.my_tp = 0
        self.my_sl = 0

        self.my_touch = False
        self.my_breakout = False

    def new_data_1_min(self):
        print("New data 1 min START:")
        para = self.bclient.get_historical_klines(
            f"{self.symbol}usdt".upper(),
            Client.KLINE_INTERVAL_1MINUTE,
            "1 day ago UTC")
        self.main_data = para
        print("================== new_data_1_min")

    def place_new_order(self, direction):
        if direction == 1:
            print("====UP======\n",
                  self.symbol,
                  self.current_order_amount,
                  self.my_ask_up,
                  self.my_sl,
                  self.my_tp)
            bot_message = f"Added new order UP {self.symbol} , \n{self.current_order_amount}, \n{round(float(self.my_ask_up), 5)},\n SL {round(float(self.my_sl), 5)} / TP {round(float(self.my_tp), 5)}"
            bot_sendtext(bot_message)
            print("\n", bot_message)
            self.order = direction
        else:
            print("====DOWN======\n",
                  self.symbol,
                  self.current_order_amount,
                  self.my_ask_down,
                  self.my_sl,
                  self.my_tp)
            bot_message = f"Added new order DOWN {self.symbol} , \n{self.current_order_amount}, \n{round(float(self.my_ask_down), 5)},\n SL {round(float(self.my_sl), 5)} / TP {round(float(self.my_tp), 5)}"
            bot_sendtext(bot_message)
            print("\n", bot_message)
            self.order = direction

    def close_order(self, direction):
        if direction == 1:
            rep = "STOP LOSS" if self.my_bid_up <= self.my_sl else "TAKE PROFIT"
            bot_message = f"QUIT order UP {self.symbol} , \n{self.current_order_amount * self.my_bid_up,}, \n{round(float(self.my_bid_up), 4)},\n {rep} \nSL {round(float(self.my_sl), 4)} / TP {round(float(self.my_tp), 4)}"
            bot_sendtext(bot_message)
            print("\n", bot_message)
            self.order = False
            self.current_order_amount = 0
        else:
            rep = "STOP LOSS" if self.my_bid_down <= self.my_sl else "TAKE PROFIT"
            bot_message = f"QUIT order DOWN {self.symbol} , \n{self.current_order_amount * self.my_bid_down,}, \n{round(float(self.my_bid_down), 4)},\n {rep} \nSL {round(float(self.my_sl), 4)} / TP {round(float(self.my_tp), 4)}"
            bot_sendtext(bot_message)
            print("\n", bot_message)
            self.order = False
            self.current_order_amount = 0

        self.my_touch = 0
        self.my_breakout = 0

    def algorithm(self):
        if not self.order:
            df = pd.DataFrame(self.main_data,
                              columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                       'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            df['close'] = pd.to_numeric(df['close'])
            df["ema25"] = ta.EMA(df['close'], timeperiod=25)
            df["ema50"] = ta.EMA(df['close'], timeperiod=50)
            df["ema100"] = ta.EMA(df['close'], timeperiod=100)

            if (df["close"].iloc[-1]) <= df["ema100"].iloc[-1] <= df["close"].iloc[-2]:
                self.my_touch = 0
                self.my_breakout = 0
            elif df["close"].iloc[-1] >= df["ema100"].iloc[-1] >= df["close"].iloc[-2]:
                self.my_touch = 0
                self.my_breakout = 0

            if df["close"].iloc[-1] > df["ema25"].iloc[-1] > df["ema50"].iloc[-1] > df["ema100"].iloc[-1]:
                self.my_touch = 1
            elif df["close"].iloc[-1] < df["ema25"].iloc[-1] < df["ema50"].iloc[-1] < df["ema100"].iloc[-1]:
                self.my_touch = 2

            if df["ema25"].iloc[-1] > df["close"].iloc[-1] > df["ema50"].iloc[-1] > df["ema100"].iloc[-1] and \
                    self.my_touch == 1 or \
                    df["ema25"].iloc[-1] > df["ema50"].iloc[-1] > df["close"].iloc[-1] > df["ema100"].iloc[-1] \
                    and self.my_touch == 1:
                self.my_breakout = 1
            elif df["ema25"].iloc[-1] < df["close"].iloc[-1] < df["ema50"].iloc[-1] < df["ema100"].iloc[-1] and \
                    self.my_touch == 2 or \
                    df["ema25"].iloc[-1] < df["ema50"].iloc[-1] < df["close"].iloc[-1] < df["ema100"].iloc[-1] \
                    and self.my_touch == 2:
                self.my_breakout = 2

            if df["close"].iloc[-1] > df["ema25"].iloc[-1] > df["ema50"].iloc[-1] > df["ema100"].iloc[-1] and \
                    self.my_breakout == 1:

                self.wallet.append(df['close'].iloc[-1])
                self.current_order_amount = self.amount / df['close'].iloc[-1] * 1.001

                self.my_sl = float(self.my_bid_up) * 0.98
                self.my_tp = float(self.my_ask_up) * 1.03
                print("======  NEW ORDER  ==========\n",
                      f"Price : {df['close'].iloc[-1]}\n",
                      f"AMOUNT : {self.amount }\n",
                      f"current_order_amount : {self.current_order_amount}\n",
                      f"my_bid_up : {self.my_bid_up}\n",
                      f"my_ask_up : {self.my_ask_up}\n",
                      f"my_sl : {self.my_sl}\n",
                      f"my_tp : {self.my_tp}\n")
                self.place_new_order(self.my_breakout)

            elif df["close"].iloc[-1] < df["ema25"].iloc[-1] < df["ema50"].iloc[-1] < df["ema100"].iloc[-1] and \
                    self.my_breakout == 2:

                self.wallet.append(df['close'].iloc[-1])
                self.current_order_amount = self.amount / df['close'].iloc[-1] * 1.001

                self.my_sl = float(self.my_bid_down) * 0.98
                self.my_tp = float(self.my_ask_down) * 1.03

                print("======  NEW ORDER  ==========\n",
                      f"Price : {df['close'].iloc[-1]}\n",
                      f"AMOUNT : {self.amount }\n",
                      f"current_order_amount : {self.current_order_amount}\n",
                      f"my_bid_down : {self.my_bid_down}\n",
                      f"my_ask_down : {self.my_ask_down}\n",
                      f"my_sl : {self.my_sl}\n",
                      f"my_tp : {self.my_tp}\n")
                self.place_new_order(self.my_breakout)

    def run(self):
        bot_sendtext("NEW BOT START")
        binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="UnicornFy")
        binance_websocket_api_manager.create_stream(['kline_1m'],
                                                    [f'{self.symbol}usdt'],
                                                    stream_label="UnicornFy",
                                                    output="UnicornFy")
        binance_websocket_api_manager.create_stream(['depth5'],
                                                    [f'{self.symbol}upusdt'],
                                                    stream_label="UnicornFy",
                                                    output="UnicornFy")
        binance_websocket_api_manager.create_stream(['depth5'],
                                                    [f'{self.symbol}downusdt'],
                                                    stream_label="UnicornFy",
                                                    output="UnicornFy")
        while True:
            if self.status:
                self.status = False
                binance_websocket_api_manager.create_stream(['kline_1m'],
                                                            [f'{self.symbol}usdt'],
                                                            stream_label="UnicornFy",
                                                            output="UnicornFy")
                binance_websocket_api_manager.create_stream(['depth5'],
                                                            [f'{self.symbol}upusdt'],
                                                            stream_label="UnicornFy",
                                                            output="UnicornFy")
                binance_websocket_api_manager.create_stream(['depth5'],
                                                            [f'{self.symbol}downusdt'],
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
                                if stream_buffer['symbol'] == f"{self.symbol.upper()}UPUSDT":
                                    self.my_ask_up = float(stream_buffer['asks'][0][0])
                                    self.my_bid_up = float(stream_buffer['bids'][0][0])

                                    # print(f"{self.symbol.upper()}UPUSDT", self.my_bid_up)

                                    if self.order == 1:
                                        if self.my_bid_up <= self.my_sl:
                                            self.close_order(self.order)
                                        elif self.my_bid_up >= self.my_tp:
                                            self.close_order(self.order)
                                else:
                                    self.my_ask_down = float(stream_buffer['asks'][0][0])
                                    self.my_bid_down = float(stream_buffer['bids'][0][0])
                                    # print(f"{self.symbol.upper()}DOWNUSDT", self.my_bid_up)
                                    if self.order == 2:
                                        if self.my_bid_down <= self.my_sl:
                                            self.close_order(self.order)
                                        elif self.my_bid_down >= self.my_tp:
                                            self.close_order(self.order)

                            if stream_buffer['event_type'] == "kline":
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

                            time.sleep(0.5)
                        except KeyError:
                            print(f"Exception :\n {stream_buffer}")
                            time.sleep(0.5)
                    else:
                        time.sleep(0.01)

                except Exception as exc:
                    self.status = True
                    traceback.print_exc()
                    time.sleep(30)


my_api = Settings.API_KEY
my_secret = Settings.API_SECRET

new_data = EmaBot("eth", 100, my_api, my_secret)

new_data.new_data_1_min()
time.sleep(1)
new_data.run()
