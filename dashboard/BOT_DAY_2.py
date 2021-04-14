import json
import time, sys, os, requests
import pandas as pd
from binance.client import Client
import traceback
from datetime import datetime
import warnings
from time import strftime
import Orders
from unicorn_fy.unicorn_fy import UnicornFy
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager

warnings.filterwarnings("ignore")
import Settings
import dbrools
import math

api_key = Settings.API_KEY
api_secret = Settings.API_SECRET
bclient = Client(api_key=api_key, api_secret=api_secret)

telega_api_key = Settings.TELEGA_KEY
telega_api_secret = Settings.TELEGA_API

sys.path.insert(0, r'/usr/local/WB')
main_path_data = os.path.expanduser('/usr/local/WB/data/')

# ################################   SHOW ALL ROWS & COLS   ####################################
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

status = False
my_data = {}
my_data_up = 0
start_price = []
madif = 0

last_usdt = 0

mk = ['ethusdt', 'ethupusdt']


def new_data():
    ETHUSDT = bclient.get_historical_klines(
        "ETHUSDT",
        Client.KLINE_INTERVAL_1MINUTE,
        "2 days ago UTC")

    for i in ETHUSDT:
        my_data[str(i[0])] = str(i[4])

    print("Finished NEW DATA")


def round_decimals_down(number: float, decimals: int = 2):
    """
    Returns a value rounded down to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)

    factor = 10 ** decimals
    return math.floor(number * factor) / factor


def bot_sendtext(bot_message):
    bot_token = telega_api_key
    bot_chat_id = telega_api_secret
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + bot_message
    requests.get(send_text)
    return


def my_sell():
    my_balance = dbrools.get_my_balances()
    my_eth = float(my_balance['ETHUP'])

    final_amount = "{:0.0{}f}".format(round_decimals_down(my_eth), 2)
    Orders.my_order(symbol="ETHUPUSDT", side=2, amount=final_amount)

    time.sleep(3)
    Orders.my_balance()
    time.sleep(2)

    my_kurs = float(my_data_up)

    my_balance2 = dbrools.get_my_balances()
    my_usdt = float(my_balance2['USDT'])

    per = round(((my_usdt - float(last_usdt)) / float(last_usdt) * 100), 2)

    print("\nSELL ETHUP >>>>>>>>", round(my_usdt, 3), ">>>>>> PROFIT :", per, "%")

    bot_sendtext(f"<<< (DayTrader SELL) >>> \n Kurs : {float(my_kurs)} \n Balance : {my_usdt}, \n Profit : {per} %")
    return


def my_buy():
    my_balance = dbrools.get_my_balances()
    my_usdt = float(my_balance['USDT'])

    if my_usdt > 20:
        my_kurs = float(my_data_up)

        amount = (my_usdt - (my_usdt / float(my_kurs) * 0.015 * float(my_kurs))) / float(my_kurs)
        final_amount = "{:0.0{}f}".format(amount, 2)
        Orders.my_order(symbol="ETHUPUSDT", side=1, amount=final_amount)
        bot_sendtext(f"<<< (DayTrader BUY)>>> \n Start : {float(my_usdt)}  \n Kurs : {float(my_kurs)} \n Balance : {round(amount, 2)}")
        time.sleep(3)
        Orders.my_balance()
        time.sleep(2)
        global last_usdt
        last_usdt = my_usdt
        print("\nBUY ETHUP >>>>>>>>", my_usdt, ">>>>>>", round(float(dbrools.get_my_balances()['ETHUP']), 3))


def signal():
    timer = list(my_data)
    prices = list(my_data.values())

    df = pd.DataFrame(data={'timestamp': timer, 'close': prices})
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    df['roll_x60'] = df["close"].rolling(60).mean()
    df['roll_x60x'] = df["roll_x60"].rolling(60).mean()
    df['roll_x5'] = df["close"].rolling(5).mean()
    df['roll_x15'] = df["close"].rolling(int(15)).mean()

    df = df.dropna()

    df["x5"] = df["roll_x5"] - df["roll_x60x"]
    df["x15"] = df["roll_x15"] - df["roll_x60x"]

    df["ttt"] = df['x5'] - df['x15']
    df["zero"] = 0

    print("DIRECTION :", df["ttt"].iloc[-1], my_data_up, ">>>>>>>>", df["x5"].iloc[-1])

    def run():
        global start_price
        if start_price:
            if df["ttt"].iloc[-1] < df["zero"].iloc[-1]:
                    start_price = []
                    my_sell()
        else:
            if df["ttt"].iloc[-1] > df["zero"].iloc[-1] and 10 > df["x5"].iloc[-1] >= 0:
                start_price = df["close"].iloc[-1]
                my_buy()
    run()


if __name__ == "__main__":
    new_data()

    binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="UnicornFy")
    binance_websocket_api_manager.create_stream(['kline_1m', "trade"], mk, stream_label="UnicornFy",
                                                output="UnicornFy")
    while True:
        if status:
            new_data()
            status = False
            binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com",
                                                                       output_default="UnicornFy")
            binance_websocket_api_manager.create_stream(['kline_1m', "trade"], mk, stream_label="UnicornFy",
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
                            if stream_buffer['symbol'] == "ETHUPUSDT":
                                if stream_buffer['event_type'] == 'trade':
                                    my_data_up = stream_buffer['price']
                            else:
                                if stream_buffer['event_type'] == 'kline':
                                    if stream_buffer['event_time'] >= stream_buffer['kline']['kline_close_time']:
                                        my_data[str(stream_buffer['kline']['kline_close_time'])] = stream_buffer['kline']['close_price']
                                        if len(my_data) > 2800:
                                            check = list(sorted(my_data.keys()))[0]
                                            del my_data[str(check)]
                                        # print(my_data_up)
                                        signal()
                        except KeyError:
                            print(f"Exception :\n {stream_buffer}")
                            time.sleep(0.5)

            except Exception as exc:
                status = True
                traceback.print_exc()
                time.sleep(30)
