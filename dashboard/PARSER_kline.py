import time, sys, os, requests
import pandas as pd
from binance.client import Client
import traceback
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")
import Settings

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
my_data_ETH = {}
my_data_LTC = {}
my_data_BTC = {}
my_data_BNB = {}


start_price = []
madif = 0

symbols = ["LTCUSDT", "ETHUSDT", "BTCUSDT", "BNBUSDT"]


def new_data():

    for i in symbols:
        # print(i, "Started")
        ETHUSDT = bclient.get_historical_klines(
            i,
            Client.KLINE_INTERVAL_1MINUTE,
            "17 days ago UTC")

        if i == symbols[1]:
            for k in ETHUSDT:
                my_data_ETH[str(k[0])] = str(k[4])
        elif i == symbols[0]:
            for k in ETHUSDT:
                my_data_LTC[str(k[0])] = str(k[4])
        elif i == symbols[2]:
            for k in ETHUSDT:
                my_data_BTC[str(k[0])] = str(k[4])
        else:
            for k in ETHUSDT:
                my_data_BNB[str(k[0])] = str(k[4])

        time.sleep(5)

    for i in symbols:
        # print(i, "Refresh")
        ETHUSDT = bclient.get_klines(
            symbol=i,
            interval=Client.KLINE_INTERVAL_1MINUTE,
            limit=5)

        if i == symbols[1]:
            for k in ETHUSDT:
                my_data_ETH[str(k[0])] = str(k[4])
        elif i == symbols[0]:
            for k in ETHUSDT:
                my_data_LTC[str(k[0])] = str(k[4])
        elif i == symbols[2]:
            for k in ETHUSDT:
                my_data_BTC[str(k[0])] = str(k[4])
        else:
            for k in ETHUSDT:
                my_data_BNB[str(k[0])] = str(k[4])
        time.sleep(1)


def bot_sendtext(bot_message):
    bot_token = telega_api_key
    bot_chat_id = telega_api_secret
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + bot_message
    requests.get(send_text)
    return


def ref_data():
    for i in symbols:
        ETHUSDT = bclient.get_klines(
            symbol=i,
            interval=Client.KLINE_INTERVAL_1MINUTE,
            limit=3)

        if i == symbols[1]:
            for k in ETHUSDT:
                my_data_ETH[str(k[0])] = str(k[4])
            if len(my_data_ETH) > 25000:
                del my_data_ETH[sorted(my_data_ETH.keys())[0]]
        elif i == symbols[0]:
            for k in ETHUSDT:
                my_data_LTC[str(k[0])] = str(k[4])
            if len(my_data_LTC) > 25000:
                del my_data_LTC[sorted(my_data_LTC.keys())[0]]
        elif i == symbols[2]:
            for k in ETHUSDT:
                my_data_BTC[str(k[0])] = str(k[4])
            if len(my_data_BTC) > 25000:
                del my_data_BTC[sorted(my_data_BTC.keys())[0]]
        else:
            for k in ETHUSDT:
                my_data_BNB[str(k[0])] = str(k[4])
            if len(my_data_BNB) > 25000:
                del my_data_BNB[sorted(my_data_BNB.keys())[0]]
        time.sleep(1)


def save_data():
    data = {"LTCUSDT": my_data_LTC,
            "ETHUSDT": my_data_ETH,
            "BTCUSDT": my_data_BTC,
            "BNBUSDT": my_data_BNB}

    for k, my_data in data.items():
        timer = list(my_data)
        prices = list(my_data.values())

        df = pd.DataFrame(data={'timestamp': timer, 'close': prices})
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        df['roll_x60'] = df["close"].rolling(60).mean()
        df['roll_x60x'] = df["roll_x60"].rolling(60).mean()

        df['roll_x5'] = df["close"].rolling(5).mean()
        df['roll_x15'] = df["close"].rolling(int(15)).mean()

        df['roll_x300'] = df["close"].rolling(int(1440 * 2)).mean()
        df['roll_x500'] = df["close"].rolling(int(1440 * 5)).mean()

        df = df.dropna()

        df["x5"] = df["roll_x5"] - df["roll_x60x"]
        df["x15"] = df["roll_x15"] - df["roll_x60x"]
        df["x21"] = df["roll_x60x"] - df["roll_x500"]
        df["x31"] = df["roll_x300"] - df["roll_x500"]

        df["ttt"] = df['x5'] - df['x15']

        df.to_csv(os.path.expanduser(f'/usr/local/WB/data/{k}.csv'), index=False)


if __name__ == "__main__":
    print(f"PARSER (kline) START at {datetime.now().strftime('%H:%M:%S')}")
    # bot_sendtext(f"PARSER (kline) START at {datetime.now().strftime('%H:%M:%S')}")
    new_data()

    while True:
        if status:
            new_data()
            status = False
            print(f"PARSER RESTART at {datetime.now().strftime('%H:%M:%S')}")
            bot_sendtext(f"PARSER RESTART at {datetime.now().strftime('%H:%M:%S')}")
        else:
            try:
                ref_data()
                if time.time() - madif > 60:
                    save_data()
                    madif = time.time()
                time.sleep(30)
            except Exception as exc:
                status = True
                traceback.print_exc()
                time.sleep(30)
