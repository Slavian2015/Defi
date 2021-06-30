import time, sys, os, requests
import pandas as pd
from binance.client import Client
import traceback
from datetime import datetime
import warnings
import talib as ta
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
import subprocess
sys.path.insert(0, r'/usr/local/WB/dashboard')
import Settings

# import dbrools

main_path_data = os.path.expanduser('/usr/local/WB/data/')
warnings.filterwarnings("ignore")

n_rools = {"BTCUSDT": {"price": 2, "decimals": 3},
           "ETHUSDT": {"price": 2, "decimals": 3},
           "BNBUSDT": {"price": 2, "decimals": 2},
           "XRPUSDT": {"price": 4, "decimals": 1},
           "LINKUSDT": {"price": 3, "decimals": 2},
           "TRXUSDT": {"price": 5, "decimals": 0},
           "EOSUSDT": {"price": 3, "decimals": 1},
           "FILUSDT": {"price": 3, "decimals": 1},
           "AAVEUSDT": {"price": 2, "decimals": 1},
           "DOTUSDT": {"price": 3, "decimals": 1},
           "UNIUSDT": {"price": 3, "decimals": 0},
           "YFIUSDT": {"price": 1, "decimals": 3},
           "SUSHIUSDT": {"price": 3, "decimals": 0},
           "BCHUSDT": {"price": 2, "decimals": 3},
           "XTZUSDT": {"price": 3, "decimals": 1},
           "LTCUSDT": {"price": 2, "decimals": 3},
           "ADAUSDT": {"price": 4, "decimals": 0},
           "XLMUSDT": {"price": 5, "decimals": 0},
           "SXPUSDT": {"price": 4, "decimals": 1},
           "1INCHUSDT": {"price": 4, "decimals": 1}}

# markets = {'xrpusdt', 'trxusdt', 'bnbusdt', 'linkusdt', 'aaveusdt'}

# markets = {'xrpusdt', 'ltcusdt', 'ethusdt', 'trxusdt', 'eosusdt', 'bnbusdt',
#            'linkusdt', 'filusdt', 'yfiusdt', 'dotusdt', 'sxpusdt', 'uniusdt',
#            'adausdt', 'aaveusdt'}
markets = {'xrpusdt'}

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
        self.min_amount = 20 * 50

        self.main_data = data_klines
        self.main_data_hour = data_klines
        # self.open_orders = data_false
        self.rsi_signal = data_false
        self.main_BD = data_false

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

    def place_new_order(self, main_direction, newsymbol, current_price):

        amount = round((self.min_amount / float(current_price)), n_rools[newsymbol]["decimals"])
        self.main_BD[newsymbol] = {"direction": main_direction, "ap": False, "amount": amount, "date": False, "tp": False, "sl": False}

        pid = subprocess.Popen(["python",
                                "/usr/local/WB/dashboard/combo_new_order.py",
                                f'--symbol={newsymbol}',
                                f'--amount={self.min_amount / float(current_price)}',
                                f'--decimals={n_rools[newsymbol]["decimals"]}',
                                f'--main_direction={main_direction}'
                                ]).pid
        return
        #
        #
        # # price = str(round(self.my_sl, n_rools[self.symbol.upper()]['price'])),
        # # amount = round(self.amount, n_rools[self.symbol.upper()]["decimals"]))
        #
        #
        #
        # if self.main_direction == 1:
        #     self.new_side = "LONG"
        # else:
        #     self.new_side = "SHORT"
        #
        # self.order = self.main_direction
        #
        # reponse = Orders.my_order_future(client=self.bclient,
        #                                  symbol=f"{self.symbol.upper()}USDT",
        #                                  side=self.main_direction,
        #                                  amount=round(self.amount, n_rools[self.symbol.upper()]["decimals"]))
        #
        # if reponse['error']:
        #     self.bot_ping = False
        #     logging.info(f"New order Error:\n {reponse}")
        #     bot_sendtext(f"New order Error:\n {reponse}")
        # else:
        #     self.order_id = reponse['result']['orderId']
        #     logging.info(f"New order:\n {reponse}")
        #     dbrools.insert_history_new(data=reponse)
        #
        #     time.sleep(1)
        #
        #     my_orders = self.bclient.futures_get_order(symbol=f"{self.symbol.upper()}USDT", orderId=self.order_id)
        #     self.my_price = float(my_orders['avgPrice'])
        #
        #     if self.order == 1:
        #         self.my_sl = self.my_price / 1.009
        #         self.my_tp = self.my_price * 1.022
        #     else:
        #         self.my_sl = self.my_price * 1.009
        #         self.my_tp = self.my_price / 1.022
        #
        #     data = {
        #         "symbol": f"{self.symbol} ({self.new_side})",
        #         "side": f"{self.new_side}",
        #         "amount": round(self.amount, n_rools[self.symbol.upper()]["decimals"]),
        #         "price": float(round(self.my_price, n_rools[self.symbol.upper()]['price'])),
        #         "direct": 'BUY',
        #         "result": 0,
        #         "date": f"{datetime.now().strftime('%d.%m.%Y')}"
        #     }
        #     dbrools.insert_history(data=data)
        #
        #     bot_message = f"Added {self.symbol} ({self.new_side}), \n{round(self.amount, n_rools[self.symbol.upper()]['decimals'])}, \n{round(self.my_price, n_rools[self.symbol.upper()]['price'])},\n SL {round(self.my_sl, n_rools[self.symbol.upper()]['price'])} / TP {round(self.my_tp, n_rools[self.symbol.upper()]['price'])}"
        #     bot_sendtext(bot_message)
        #     print("\n", bot_message)
        #
        #     self.place_tp_order()

    def place_tp_sl(self, newsymbol, my_price, my_date):

        if self.main_BD[newsymbol]['direction'] == 1:
            my_sl = my_price / 1.01
            my_tp = my_price * 1.021
        else:
            my_sl = my_price * 1.01
            my_tp = my_price / 1.021

        self.main_BD[newsymbol]['ap'] = my_price
        self.main_BD[newsymbol]['date'] = my_date
        self.main_BD[newsymbol]['tp'] = my_tp
        self.main_BD[newsymbol]['sl'] = my_sl

        pid = subprocess.Popen(["python",
                                "/usr/local/WB/dashboard/combo_orders.py",
                                f'--symbol={newsymbol}',
                                f'--amount={self.main_BD[newsymbol]["amount"]}',
                                f'--decimalsp={n_rools[newsymbol]["price"]}',
                                f'--decimals={n_rools[newsymbol]["decimals"]}',
                                f'--main_direction={self.main_BD[newsymbol]["direction"]}'
                                f'--my_sl={my_sl}',
                                f'--my_tp={my_tp}',
                                ]).pid



        data = {
            "symbol": f"{self.symbol} ({self.new_side})",
            "side": f"{self.new_side}",
            "amount": round(self.amount, n_rools[self.symbol.upper()]["decimals"]),
            "price": float(round(self.my_price, n_rools[self.symbol.upper()]['price'])),
            "direct": 'BUY',
            "result": 0,
            "date": f"{my_date}"
        }
        dbrools.insert_history(data=data)

        bot_message = f"Added {self.symbol} ({self.new_side}), \n{round(self.amount, n_rools[self.symbol.upper()]['decimals'])}, \n{round(self.my_price, n_rools[self.symbol.upper()]['price'])},\n SL {round(self.my_sl, n_rools[self.symbol.upper()]['price'])} / TP {round(self.my_tp, n_rools[self.symbol.upper()]['price'])}"
        bot_sendtext(bot_message)
        print("\n", bot_message)


        return

    def algorithm(self, current_symbol):
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
                if not self.main_BD[current_symbol]:
                    self.place_new_order(my_RSI, current_symbol, df["close"].iloc[-1])
        elif self.my_Stoch[current_symbol] == 2 and my_RSI == 2:
            if df["hist"].iloc[-1] < 0 < df["hist"].iloc[-2] and self.rsi_signal[current_symbol] < 30:
                if not self.main_BD[current_symbol]:
                    self.place_new_order(my_RSI, current_symbol, df["close"].iloc[-1])

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
        self.binance_websocket_api_manager_future = BinanceWebSocketApiManager(exchange="binance.com-futures",
                                                                        output_default="dict")

        self.binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h'],
                                                         markets,
                                                         stream_label="UnicornFy",
                                                         output="UnicornFy")

        self.binance_websocket_api_manager_future.create_stream('arr', '!userData',
                                                         api_key=self.api_key, api_secret=self.api_secret,
                                                         output="dict")

        while self.bot_ping:
            if self.status:
                self.status = False
                self.binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h'],
                                                                 markets,
                                                                 stream_label="UnicornFy",
                                                                 output="UnicornFy")

                self.binance_websocket_api_manager_future.create_stream('arr', '!userData',
                                                                 api_key=self.api_key, api_secret=self.api_secret,
                                                                 output="dict")

                print(f"PARSER RESTART at {datetime.now().strftime('%H:%M:%S')}")
            else:
                try:
                    if self.binance_websocket_api_manager.is_manager_stopping() or self.binance_websocket_api_manager_future.is_manager_stopping():
                        exit(0)
                        self.status = True
                    stream_buffer = self.binance_websocket_api_manager.pop_stream_data_from_stream_buffer()

                    stream_buffer_future = self.binance_websocket_api_manager_future.pop_stream_data_from_stream_buffer()

                    if stream_buffer_future is False:
                        pass
                    else:
                        if stream_buffer_future is not None:
                            try:
                                # print("\nstream_buffer_future :\n", stream_buffer_future)
                                if "e" in stream_buffer_future:
                                    print("\n<<<<<<  e  >>>>>> :\n", stream_buffer_future)
                            except KeyError:
                                print(f"Exception FUTURE:\n {stream_buffer}")
                                time.sleep(0.5)
                    if stream_buffer is False:
                        time.sleep(0.01)
                    else:
                        if stream_buffer is not None:
                            try:
                                # print("\nstream_buffer :\n", stream_buffer)
                                # if "e" in stream_buffer:
                                #     pass
                                #     # if stream_buffer['e'] == 'ACCOUNT_UPDATE':
                                #     #     if stream_buffer['a']['P'][0]['s'] == f'{self.symbol}usdt'.upper() and stream_buffer['a']['P'][0]['pa'] == "0":
                                #     #         if self.order == 1:
                                #     #             if self.trade >= self.my_price:
                                #     #                 self.close_tp_order()
                                #     #             if self.trade < self.my_price:
                                #     #                 self.close_sl_order()
                                #     #         elif self.order == 2:
                                #     #             if self.trade > self.my_price:
                                #     #                 self.close_sl_order()
                                #     #             if self.trade <= self.my_price:
                                #     #                 self.close_tp_order()
                                # else:
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
