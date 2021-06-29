import json
import time, sys, os, requests
import pandas as pd
import numpy as np
from binance.client import Client
import traceback
from datetime import datetime
import warnings
import logging
from unicorn_fy.unicorn_fy import UnicornFy
from time import strftime
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
import argparse

sys.path.insert(0, r'/usr/local/WB/dashboard')
import Orders
import dbrools
from zigzag import peak_valley_pivots

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
        self.main_symbol_up = f'{self.symbol}upusdt'
        self.main_symbol_down = f'{self.symbol}downusdt'
        self.rep = 0

        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.bclient = Client(api_key=self.api_key, api_secret=self.api_secret)
        self.bot_ping = True
        self.status = False

        self.main_data = []
        self.my_ask_up = 0
        self.my_bid_up = 0
        self.my_ask_down = 0
        self.my_bid_down = 0

        self.min_amount = min_amount
        self.amount_up = 0
        self.amount_down = 0

        self.grid_qty = 5
        self.last_rep = 1

        self.up_orders = {}
        self.down_orders = {}
        self.num_order = 0

        # self.main_direction = 1 if my_direction == "buy" else 2
        # self.new_side = "UP" if my_direction == "buy" else "DOWN"
        # self.wallet = []
        #
        # self.order = False
        # self.order_id = False
        # self.order_time = False
        # self.order_price = 0

        self.my_sl = -3

    def new_data_1_min(self):
        print("New data 1 min START:")
        para = self.bclient.get_historical_klines(
            f"{self.symbol}usdt".upper(),
            Client.KLINE_INTERVAL_1MINUTE,
            "1 day ago UTC")
        self.main_data = para
        print("================== new_data_1_min")

    def place_new_order(self, n):
        bot_message = f"Added {self.symbol}{self.new_side} , \n{round(self.amount, 2)}, \n{round(float(self.my_ask), 5)},\n SL {round(float(self.my_sl), 5)} / TP {round(float(self.my_tp), 5)}"
        bot_sendtext(bot_message)
        print("\n", bot_message)
        self.order = self.main_direction

        reponse = Orders.my_order(client=self.bclient,
                                  symbol=f"{self.symbol.upper()}{self.new_side}USDT",
                                  side=1,
                                  amount=round(self.amount, 2))

        if reponse['error']:
            self.bot_ping = False
            logging.info(f"New order Error:\n {reponse}")
            bot_sendtext(f"New order Error:\n {reponse}")
        else:
            self.order_id = reponse['result']['orderId']
            logging.info(f"New order:\n {reponse}")
            dbrools.insert_history_new(data=reponse)
            self.order_price = self.my_bid
            data = {
                "symbol": f"{self.symbol}{self.new_side}",
                "amount": round(self.amount, 2),
                "price": self.my_ask,
                "direct": 'BUY',
                "result": 0,
                "date": f"{datetime.now().strftime('%d.%m.%Y')}"
            }
            dbrools.insert_history(data=data)
            self.order_time = time.time()
            self.place_tp_order()

    def place_tp_order(self):
        reponse = Orders.my_order(client=self.bclient,
                                  symbol=self.main_symbol.upper(),
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
        df = pd.DataFrame(self.main_data,
                          columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                   'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        X = df['close'].values
        pivots = peak_valley_pivots(X, 0.02, -0.02)

        if np.arange(len(X))[pivots == 1][-1] >= np.arange(len(X))[pivots == -1][-1] and \
                np.arange(len(X))[pivots == 1][-2] >= np.arange(len(X))[pivots == -1][-1]:
            self.rep = 1
        elif np.arange(len(X))[pivots == -1][-1] >= np.arange(len(X))[pivots == 1][-1] and \
                np.arange(len(X))[pivots == -1][-2] >= np.arange(len(X))[pivots == 1][-1]:
            self.rep = 2
        else:
            self.rep = 3

        if wallet_up:
            diff = (sum(wallet_up) * df['close'].iloc[ind] - len(wallet_up) * my_lot) / (len(wallet_up) * my_lot) * 100

            if rep == 3 and last_rep != 3:
                total.append(len(wallet_up) * my_lot * diff / 100)
                start_balance = start_balance + len(wallet_up) * my_lot * diff / 100
                total_order_qty.append(len(wallet_up)+1)
                if my_print:
                    print(len(wallet_up), "(total orders in a raw) ", round((ind - start_ind), 2), " bars |",
                          " balance :", round((len(wallet_up) * my_lot * diff / 100), 2), "=====>>>>>  UP")
                wallet_up = []
                up_orders = {}
                last_rep = 1

                for kr, v in enumerate([1, 1.01, 1.02, 1.03, 1.04]):
                    down_orders[kr+1] = df["close"].iloc[ind] * v
                start_ind = ind
                order_qty += 1
                wallet_down.append(my_lot / df['close'].iloc[ind])
                num_order = 1

            else:
                if num_order <= grid_qty-1:
                    # print("UP ORDERS ================>>>>>>>>> :", up_orders)
                    if df['close'].iloc[ind] <= up_orders[num_order+1]:
                        wallet_up.append(my_lot / up_orders[num_order+1])
                        num_order += 1
                elif num_order == grid_qty:
                    if diff < my_sl:
                        total.append(len(wallet_up) * my_lot * my_sl / 100)
                        start_balance = start_balance + len(wallet_up) * my_lot * my_sl / 100
                        total_order_qty.append(len(wallet_up)+1)
                        if my_print:
                            print(round((ind - start_ind), 2), " bars |", " balance :",
                                  round((len(wallet_up) * my_lot * my_sl / 100), 2), "=====>>>>>  STOP LOSS")

                        wallet_up = []
                        up_orders = {}
                        last_rep = 2
        elif wallet_down:
            diff = (len(wallet_down) * my_lot - sum(wallet_down) * df['close'].iloc[ind]) / (len(wallet_down) * my_lot) * 100
            if rep == 3 and last_rep != 3:
                total.append(len(wallet_down) * my_lot * diff / 100)
                start_balance = start_balance + len(wallet_down) * my_lot * diff / 100
                total_order_qty.append(len(wallet_down)+1)
                if my_print:
                    print(len(wallet_down), "(total orders in a raw) ", round((ind - start_ind), 2), " bars |",
                          " balance :", round((len(wallet_down) * my_lot * diff / 100), 2), "=====>>>>>  DOWN")
                wallet_down = []
                down_orders = {}

                for kr, v in enumerate([1, 1.01, 1.02, 1.03, 1.04]):
                    up_orders[kr+1] = df["close"].iloc[ind] / v
                start_ind = ind
                order_qty += 1
                wallet_up.append(my_lot / df['close'].iloc[ind])
                num_order = 1
                last_rep = 2

            else:
                if num_order <= grid_qty-1:
                    if df['close'].iloc[ind] <= down_orders[num_order+1]:
                        wallet_down.append(my_lot / down_orders[num_order+1])
                        num_order += 1
                elif num_order == grid_qty:
                    if diff < my_sl:
                        total.append(len(wallet_down) * my_lot * my_sl / 100)
                        start_balance = start_balance + len(wallet_down) * my_lot * my_sl / 100
                        total_order_qty.append(len(wallet_down)+1)
                        if my_print:
                            print(round((ind - start_ind), 2), " bars |", " balance :",
                                  round((len(wallet_down) * my_lot * my_sl / 100), 2), "=====>>>>>  STOP LOSS")
                        wallet_down = []
                        down_orders = {}
                        last_rep = 1
        else:
            if self.rep == 3 and self.last_rep == 2:
                for kr, v in enumerate([1, 1.01, 1.02, 1.03, 1.04]):
                    self.down_orders[kr+1] = df["close"].iloc[-1] * v
                self.place_new_order(2)
                # wallet_down.append(my_lot / df['close'].iloc[-1])
                self.num_order = 1
                self.last_rep = 1
            elif self.rep == 3 and self.last_rep == 1:
                for kr, v in enumerate([1, 1.01, 1.02, 1.03, 1.04]):
                    self.up_orders[kr+1] = df["close"].iloc[-1] / v

                self.place_new_order(1)
                # wallet_up.append(my_lot / df['close'].iloc[-1])
                self.num_order = 1
                self.last_rep = 2


            # if self.order:
            #     if self.my_ask > self.my_tp:
            #         self.close_tp_order()
            #         """ проверить по ID и сохранить ордер в БД"""
            #     if self.my_bid <= self.my_sl:
            #         """ отменить TP, Проверить и сохранить ордер в БД"""
            #         self.close_sl_order()

            # if self.my_Stoch == self.main_direction and self.my_RSI == self.main_direction:
            #     if self.main_direction == 1:
            #         my_signal = df["hist"].iloc[-1] > 0 > df["hist"].iloc[-2]
            #     else:
            #         my_signal = df["hist"].iloc[-1] < 0 < df["hist"].iloc[-2]
            #
            #     if my_signal and self.supertrend_signal == self.main_direction:
            #         self.wallet.append(self.amount)
            #         self.my_sl = self.my_bid / 1.018
            #         self.my_tp = self.my_ask * 1.05
            #         self.place_new_order()


    def run(self):
        bot_sendtext(f"ZigZag {self.symbol} START")
        binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="UnicornFy")
        binance_websocket_api_manager.create_stream(['kline_1m'],
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
                binance_websocket_api_manager.create_stream(['kline_1m'],
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
                                if stream_buffer['symbol'] == self.main_symbol_up.upper():
                                    self.my_ask_up = float(stream_buffer['asks'][0][0])
                                    self.my_bid_up = float(stream_buffer['bids'][0][0])
                                    self.amount_up = self.min_amount / float(stream_buffer['asks'][0][0])
                                elif stream_buffer['symbol'] == self.main_symbol_down.upper():
                                    self.my_ask_down = float(stream_buffer['asks'][0][0])
                                    self.my_bid_down = float(stream_buffer['bids'][0][0])
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
                        except KeyError:
                            print(f"Exception :\n {stream_buffer}")
                            time.sleep(0.5)
                            bot_sendtext(f"ZigZag {self.symbol} Exception :\n {stream_buffer}")
                    else:
                        time.sleep(0.01)
                except Exception as exc:
                    self.status = True
                    traceback.print_exc()
                    bot_sendtext(f"ZigZag {self.symbol} Exception :\n {exc}")
                    time.sleep(30)


new_keys = dbrools.my_keys.find_one()

telega_api_key = new_keys['telega']['key']
telega_api_secret = new_keys['telega']['secret']
api_key = new_keys['bin']['key']
api_secret = new_keys['bin']['secret']


new_data = SsrmBot(args.symbol, float(args.amount), api_key, api_secret, args.side)
new_data.new_data_1_min()
time.sleep(1)
new_data.run()
