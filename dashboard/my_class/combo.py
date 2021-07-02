import time, sys, os, requests
import pandas as pd
from binance.client import Client
import traceback
from datetime import datetime
import warnings
import talib as ta
import logging
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
import subprocess

sys.path.insert(0, r'/usr/local/WB/dashboard')
import json
import dbrools

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

main_path_settings = f'/usr/local/WB/dashboard/data/settings.json'

a_file1 = open(main_path_settings, "r")
rools = json.load(a_file1)
a_file1.close()
active_list = []

for k, v in rools.items():
    if v:
        active_list.append(k.lower())

markets = set(active_list)

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
        self.rsi_signal = data_false
        self.main_BD = data_false
        self.my_Stoch = data_false

        self.binance_websocket_api_manager = None
        self.binance_websocket_api_manager_future = None
        self.status = False

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
        self.main_BD[newsymbol] = {"direction": main_direction, "ap": False, "amount": amount, "date": False,
                                   "tp": False, "sl": False}

        pid = subprocess.Popen(["python",
                                "/usr/local/WB/dashboard/combo_new_order.py",
                                f'--symbol={newsymbol}',
                                f'--amount={self.min_amount / float(current_price)}',
                                f'--decimals={n_rools[newsymbol]["decimals"]}',
                                f'--main_direction={main_direction}'
                                ]).pid

        bot_message = f"Added {newsymbol} ({'LONG' if main_direction == 1 else 'SHORT'})"
        bot_sendtext(bot_message)
        print("\n", bot_message)
        return

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
        return

    def close_position(self, newsymbolf, my_profitf):

        pid = subprocess.Popen(["python",
                                "/usr/local/WB/dashboard/combo_cancel_order.py",
                                f'--symbol={newsymbolf}',
                                f'--my_profitf={my_profitf}'
                                ]).pid

        new_side = 'LONG' if self.main_BD[newsymbolf]['main_direction'] == 1 else 'SHORT'
        if float(my_profitf) > 0:
            bot_message = f"TAKE PROFIT ({my_profitf})\n {newsymbolf} ({new_side})"
            result = 1
            priceout = round(self.main_BD[newsymbolf]['tp'], n_rools[newsymbolf]['price'])
        else:
            bot_message = f"STOP LOSS ({my_profitf})\n {newsymbolf} ({new_side})"
            result = 2
            priceout = round(self.main_BD[newsymbolf]['sl'], n_rools[newsymbolf]['price'])
        bot_sendtext(bot_message)

        print("\n", bot_message)
        data = {
            "symbol": newsymbolf,
            "side": new_side,
            "priceIn": round(self.main_BD[newsymbolf]['ap'], n_rools[newsymbolf]['price']),
            "priceOut": priceout,
            "result": result,
            "profit": float(my_profitf),
            "date": f"{self.main_BD[newsymbolf]['date']}"
        }
        dbrools.insert_new_history(data=data)

        logging.info(f"\nClosed_position:\n {data}")
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

        bot_sendtext(f"NEW FUTURE START")
        self.binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com",
                                                                        output_default="dict")
        self.binance_websocket_api_manager_future = BinanceWebSocketApiManager(exchange="binance.com-futures",
                                                                               output_default="dict")

        self.binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h'],
                                                         markets,
                                                         stream_label="UnicornFy",
                                                         output="UnicornFy")

        self.binance_websocket_api_manager_future.create_stream('arr', '!userData',
                                                                api_key=self.api_key,
                                                                api_secret=self.api_secret,
                                                                output="dict")

        while self.bot_ping:
            if self.status:
                self.status = False
                self.binance_websocket_api_manager.create_stream(['kline_1m', 'kline_1h'],
                                                                 markets,
                                                                 stream_label="UnicornFy",
                                                                 output="UnicornFy")

                self.binance_websocket_api_manager_future.create_stream('arr', '!userData',
                                                                        api_key=self.api_key,
                                                                        api_secret=self.api_secret,
                                                                        output="dict")

                print(f"PARSER RESTART at {datetime.now().strftime('%H:%M:%S')}")
                logging.warning(f"PARSER RESTART at {datetime.now().strftime('%H:%M:%S')}")
            else:
                try:
                    if self.binance_websocket_api_manager.is_manager_stopping() or self.binance_websocket_api_manager_future.is_manager_stopping():
                        exit(0)
                        self.status = True
                        logging.error('WEBSOCKET is_manager_stopping')
                    stream_buffer = self.binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
                    stream_buffer_future = self.binance_websocket_api_manager_future.pop_stream_data_from_stream_buffer()
                    if stream_buffer_future is False:
                        pass
                    else:
                        if stream_buffer_future is not None:
                            try:
                                if stream_buffer_future['e'] == 'ACCOUNT_UPDATE':
                                    # print(stream_buffer_future)
                                    if float(stream_buffer_future['a']['P'][0]['ep']) > 0 and \
                                            float(stream_buffer_future['a']['P'][0]['up']) == 0:
                                        newsymbolf = stream_buffer_future['a']['P'][0]['s']
                                        my_pricef = stream_buffer_future['a']['P'][0]['ep']
                                        my_datef = stream_buffer_future['T']
                                        print('Place_tp_sl')
                                        logging.warning(f"Place_tp_sl {stream_buffer_future['a']['P'][0]['s']}")
                                        self.place_tp_sl(newsymbolf, my_pricef, my_datef)
                                    elif float(stream_buffer_future['a']['P'][0]['ep']) == 0 and \
                                            float(stream_buffer_future['a']['P'][0]['up']) == 0:
                                        self.main_BD[stream_buffer_future['a']['P'][0]['s']] = False
                                        print('Clean main_BD')
                                        logging.warning(f"Clean main_BD {stream_buffer_future['a']['P'][0]['s']}")
                                    else:
                                        newsymbolf = stream_buffer_future['a']['P'][0]['s']
                                        my_profitf = stream_buffer_future['a']['P'][0]['up']
                                        print('Close_position')
                                        logging.warning(f'Close_position {newsymbolf}, {my_profitf}')
                                        self.close_position(newsymbolf, my_profitf)
                            except KeyError:
                                print(f"Exception KeyError FUTURE:\n {stream_buffer}")
                                logging.error(f"Exception KeyError FUTURE:\n {stream_buffer}")
                                time.sleep(0.5)
                    if stream_buffer is False:
                        time.sleep(0.01)
                    else:
                        if stream_buffer is not None:
                            try:
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
                                        if self.main_data[stream_buffer["symbol"]][-1][-6] != stream_buffer['kline'][
                                            'kline_close_time']:
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
                                        if self.main_data_hour[stream_buffer["symbol"]][-1][-6] != \
                                                stream_buffer['kline']['kline_close_time']:
                                            self.main_data_hour[stream_buffer["symbol"]].append(new_row)
                                            del self.main_data_hour[stream_buffer["symbol"]][0]
                                            self.algorithm_rsi(stream_buffer["symbol"])
                                time.sleep(0.01)
                            except KeyError:
                                print(f"Exception :\n {stream_buffer}")
                                logging.error(f"Exception :\n {stream_buffer}")
                                time.sleep(0.5)
                except Exception as exc:
                    self.status = True
                    traceback.print_exc()
                    bot_sendtext(f"NEW FUTURE Exception : \n {exc}")
                    print(f"NEW FUTURE Exception : \n {exc}")
                    logging.error(f"NEW FUTURE Exception : \n {exc}")
                    time.sleep(30)


new_keys = dbrools.my_keys.find_one()

telega_api_key = new_keys['telega']['key']
telega_api_secret = new_keys['telega']['secret']
api_key = new_keys['bin']['key']
api_secret = new_keys['bin']['secret']

new_data = SsrmBot()

new_data.new_data_1_hour()
new_data.new_data_1_min()
time.sleep(1)
new_data.run()
