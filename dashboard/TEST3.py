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


###########################

bot_ping = True
binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures",
                                                           output_default="dict")
# binance_websocket_api_manager.create_stream(['kline_1m'],
#                                                  ['trxusdt'],
#                                                  stream_label="UnicornFy",
#                                                  output="UnicornFy")
#
# binance_websocket_api_manager.create_stream(['trade'],
#                                             ['trxusdt'],
#                                             output="UnicornFy")

binance_websocket_api_manager.create_stream('arr', '!userData',
                                            api_key=api_key, api_secret=api_secret,
                                            output="dict"
                                            )

while bot_ping:
    stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
    try:
        if binance_websocket_api_manager.is_manager_stopping():
            exit(0)
            bot_ping = False
            print("bot_ping", bot_ping)
        if stream_buffer:

            if "e" in stream_buffer:
                if stream_buffer['e'] == 'ACCOUNT_UPDATE':
                    print(stream_buffer, "\n===========================================================")

            # try:
            #     if stream_buffer['event_type'] == "trade":
            #         my_ask = float(stream_buffer['price'])
            #         my_bid = float(stream_buffer['quantity'])
            #         # pass
            #         print("\n===========================================================\n", "trade\n", my_ask, my_bid)
            #     else:
            #         pass
            #         # print("\n===========================================================\n", "kline\n", stream_buffer)
            #     # print(stream_buffer, "\n===========================================================")
            #     # time.sleep(2)
            # except KeyError:
            #     print(f"Exception :\n {stream_buffer}")
        time.sleep(1)
    except Exception as exc:
        bot_ping = False
        traceback.print_exc()
        time.sleep(1)


# s = {'stream': 'trxusdt@depth5'}
#
# if "depth5" in s['stream']:
#     print("depth5")
# else:
#     print("NO")



"""
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
import logging
import time
import threading
import os


def print_stream_data_from_stream_buffer(binance_websocket_api_manager):
    while True:
        if binance_websocket_api_manager.is_manager_stopping():
            exit(0)
        oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
        if oldest_stream_data_from_stream_buffer is False:
            time.sleep(0.01)
        else:
            print(oldest_stream_data_from_stream_buffer)


# create instances of BinanceWebSocketApiManager
ubwa_com_im = BinanceWebSocketApiManager(exchange="binance.com-futures")

# create the userData streams
user_stream_id_im = ubwa_com_im.create_stream('!userData', "trxusdt", api_key=api_key, api_secret=api_secret)

# start a worker process to move the received stream_data from the stream_buffer to a print function
worker_thread = threading.Thread(target=print_stream_data_from_stream_buffer, args=(ubwa_com_im,))
worker_thread.start()

# monitor the streams
while True:
    # ubwa_com_im.print_stream_info(user_stream_id_im)
    time.sleep(1)
"""


"""
Closed Position

{'e': 'ORDER_TRADE_UPDATE', 'T': 1622812358247, 'E': 1622812358253, 'o': {'s': 'TRXUSDT', 'c': 'web_st_FrDgRbUPFFGs951', 'S': 'SELL', 'o': 'STOP_MARKET', 'f': 'GTE_GTC', 'q': '150', 'p': '0', 'ap': '0', 'sp': '0.07550', 'x': 'EXPIRED', 'X': 'EXPIRED', 'i': 4014205630, 'l': '0', 'z': '0', 'L': '0', 'T': 1622812358247, 't': 0, 'b': '0', 'a': '0', 'm': False, 'R': True, 'wt': 'MARK_PRICE', 'ot': 'STOP_MARKET', 'ps': 'BOTH', 'cp': False, 'rp': '0', 'pP': True, 'si': 25305715, 'ss': 3, 'st': 'OTOCO'}} 
===========================================================
{'e': 'ORDER_TRADE_UPDATE', 'T': 1622812358247, 'E': 1622812358253, 'o': {'s': 'TRXUSDT', 'c': 'web_st_rRii3jh4cJc6RpC', 'S': 'SELL', 'o': 'TAKE_PROFIT_MARKET', 'f': 'GTE_GTC', 'q': '150', 'p': '0', 'ap': '0', 'sp': '0.07650', 'x': 'EXPIRED', 'X': 'EXPIRED', 'i': 4014205629, 'l': '0', 'z': '0', 'L': '0', 'T': 1622812358247, 't': 0, 'b': '0', 'a': '0', 'm': False, 'R': True, 'wt': 'MARK_PRICE', 'ot': 'TAKE_PROFIT_MARKET', 'ps': 'BOTH', 'cp': False, 'rp': '0', 'pP': True, 'si': 25305715, 'ss': 2, 'st': 'OTOCO'}} 
===========================================================
{'e': 'ORDER_TRADE_UPDATE', 'T': 1622812358247, 'E': 1622812358253, 'o': {'s': 'TRXUSDT', 'c': 'web_73cPJrYDmm232j136Iui', 'S': 'SELL', 'o': 'MARKET', 'f': 'GTC', 'q': '150', 'p': '0', 'ap': '0', 'sp': '0', 'x': 'NEW', 'X': 'NEW', 'i': 4014218898, 'l': '0', 'z': '0', 'L': '0', 'T': 1622812358247, 't': 0, 'b': '0', 'a': '0', 'm': False, 'R': True, 'wt': 'CONTRACT_PRICE', 'ot': 'MARKET', 'ps': 'BOTH', 'cp': False, 'rp': '0', 'pP': False, 'si': 0, 'ss': 0}} 
===========================================================
{'e': 'ACCOUNT_UPDATE', 'T': 1622812358247, 'E': 1622812358254, 'a': {'B': [{'a': 'USDT', 'wb': '316.14003714', 'cw': '316.14003714', 'bc': '0'}], 'P': [{'s': 'TRXUSDT', 'pa': '0', 'ep': '0.00000', 'cr': '25.85272001', 'up': '0', 'mt': 'isolated', 'iw': '0', 'ps': 'BOTH', 'ma': 'USDT'}], 'm': 'ORDER'}} 
===========================================================
{'e': 'ORDER_TRADE_UPDATE', 'T': 1622812358247, 'E': 1622812358254, 'o': {'s': 'TRXUSDT', 'c': 'web_73cPJrYDmm232j136Iui', 'S': 'SELL', 'o': 'MARKET', 'f': 'GTC', 'q': '150', 'p': '0', 'ap': '0.07596', 'sp': '0', 'x': 'TRADE', 'X': 'FILLED', 'i': 4014218898, 'l': '150', 'z': '150', 'L': '0.07596', 'n': '0.00455760', 'N': 'USDT', 'T': 1622812358247, 't': 133745829, 'b': '0', 'a': '0', 'm': False, 'R': True, 'wt': 'CONTRACT_PRICE', 'ot': 'MARKET', 'ps': 'BOTH', 'cp': False, 'rp': '-0.00150000', 'pP': False, 'si': 0, 'ss': 0}} 

"""


"""
STOP LOSS
{"e":"ORDER_TRADE_UPDATE","T":1622812021756,"E":1622812021758,"o":{"s":"TRXUSDT","c":"web_st_Ihlt5wPQEpiqt1j","S":"SELL","o":"MARKET","f":"GTC","q":"150","p":"0","ap":"0","sp":"0","x":"NEW","X":"NEW","i":4014170256,"l":"0","z":"0","L":"0","T":1622812021756,"t":0,"b":"0","a":"0","m":false,"R":false,"wt":"CONTRACT_PRICE","ot":"MARKET","ps":"BOTH","cp":false,"rp":"0","pP":false,"si":25304722,"ss":1,"st":"OTOCO"}}


{"e":"ACCOUNT_UPDATE","T":1622812021756,"E":1622812021758,"a":{"B":[{"a":"USDT","wb":"316.19421294","cw":"304.83274584","bc":"0"}],"P":[{"s":"TRXUSDT","pa":"-150","ep":"0.07574","cr":"25.89322001","up":"-0.00501150","mt":"isolated","iw":"11.36146710","ps":"BOTH","ma":"USDT"}],"m":"ORDER"}}
{"e":"ORDER_TRADE_UPDATE","T":1622812021756,"E":1622812021758,"o":{"s":"TRXUSDT","c":"web_st_Ihlt5wPQEpiqt1j","S":"SELL","o":"MARKET","f":"GTC","q":"150","p":"0","ap":"0.07574","sp":"0","x":"TRADE","X":"FILLED","i":4014170256,"l":"150","z":"150","L":"0.07574","n":"0.00454439","N":"USDT","T":1622812021756,"t":133743970,"b":"0","a":"0","m":false,"R":false,"wt":"CONTRACT_PRICE","ot":"MARKET","ps":"BOTH","cp":false,"rp":"0","pP":false,"si":25304722,"ss":1,"st":"OTOCO"}}
{"e":"ORDER_TRADE_UPDATE","T":1622812021759,"E":1622812021761,"o":{"s":"TRXUSDT","c":"web_st_VjMqi9dr7NULDpU","S":"BUY","o":"TAKE_PROFIT_MARKET","f":"GTE_GTC","q":"150","p":"0","ap":"0","sp":"0.07550","x":"NEW","X":"NEW","i":4014170258,"l":"0","z":"0","L":"0","T":1622812021759,"t":0,"b":"0","a":"0","m":false,"R":true,"wt":"MARK_PRICE","ot":"TAKE_PROFIT_MARKET","ps":"BOTH","cp":false,"rp":"0","pP":true,"si":25304722,"ss":2,"st":"OTOCO"}}

{"e":"ORDER_TRADE_UPDATE","T":1622812021759,"E":1622812021761,"o":{"s":"TRXUSDT","c":"web_st_U8qk7AIsi5rYhlu","S":"BUY","o":"STOP_MARKET","f":"GTE_GTC","q":"150","p":"0","ap":"0","sp":"0.07600","x":"NEW","X":"NEW","i":4014170259,"l":"0","z":"0","L":"0","T":1622812021759,"t":0,"b":"0","a":"0","m":false,"R":true,"wt":"MARK_PRICE","ot":"STOP_MARKET","ps":"BOTH","cp":false,"rp":"0","pP":true,"si":25304722,"ss":3,"st":"OTOCO"}}
{"e":"ORDER_TRADE_UPDATE","T":1622812118021,"E":1622812118026,"o":{"s":"TRXUSDT","c":"web_st_U8qk7AIsi5rYhlu","S":"BUY","o":"STOP_MARKET","f":"GTE_GTC","q":"150","p":"0","ap":"0","sp":"0.07600","x":"EXPIRED","X":"EXPIRED","i":4014170259,"l":"0","z":"0","L":"0","T":1622812118021,"t":0,"b":"0","a":"0","m":false,"R":true,"wt":"MARK_PRICE","ot":"STOP_MARKET","ps":"BOTH","cp":false,"rp":"0","pP":true,"si":25304722,"ss":3,"st":"OTOCO"}}

{"e":"ORDER_TRADE_UPDATE","T":1622812118021,"E":1622812118026,"o":{"s":"TRXUSDT","c":"web_st_U8qk7AIsi5rYhlu","S":"BUY","o":"MARKET","f":"GTC","q":"150","p":"0","ap":"0","sp":"0.07600","x":"NEW","X":"NEW","i":4014170259,"l":"0","z":"0","L":"0","T":1622812118021,"t":0,"b":"0","a":"0","m":false,"R":true,"wt":"MARK_PRICE","ot":"STOP_MARKET","ps":"BOTH","cp":false,"rp":"0","pP":false,"si":25304722,"ss":3,"st":"OTOCO"}}

{"e":"ACCOUNT_UPDATE","T":1622812118021,"E":1622812118026,"a":{"B":[{"a":"USDT","wb":"316.15065294","cw":"316.15065294","bc":"0"}],"P":[{"s":"TRXUSDT","pa":"0","ep":"0.00000","cr":"25.85422001","up":"0","mt":"isolated","iw":"0","ps":"BOTH","ma":"USDT"}],"m":"ORDER"}}
{"e":"ORDER_TRADE_UPDATE","T":1622812118021,"E":1622812118026,"o":{"s":"TRXUSDT","c":"web_st_U8qk7AIsi5rYhlu","S":"BUY","o":"MARKET","f":"GTC","q":"150","p":"0","ap":"0.07600","sp":"0.07600","x":"TRADE","X":"FILLED","i":4014170259,"l":"150","z":"150","L":"0.07600","n":"0.00456000","N":"USDT","T":1622812118021,"t":133744542,"b":"0","a":"0","m":false,"R":true,"wt":"MARK_PRICE","ot":"STOP_MARKET","ps":"BOTH","cp":false,"rp":"-0.03900000","pP":false,"si":25304722,"ss":3,"st":"OTOCO"}}
{"e":"ORDER_TRADE_UPDATE","T":1622812118021,"E":1622812118026,"o":{"s":"TRXUSDT","c":"web_st_VjMqi9dr7NULDpU","S":"BUY","o":"TAKE_PROFIT_MARKET","f":"GTE_GTC","q":"150","p":"0","ap":"0","sp":"0.07550","x":"EXPIRED","X":"EXPIRED","i":4014170258,"l":"0","z":"0","L":"0","T":1622812118021,"t":0,"b":"0","a":"0","m":false,"R":true,"wt":"MARK_PRICE","ot":"TAKE_PROFIT_MARKET","ps":"BOTH","cp":false,"rp":"0","pP":true,"si":25304722,"ss":2,"st":"OTOCO"}}


"""


d = {"e":"ORDER_TRADE_UPDATE","T":1622812021756,"E":1622812021758,"o":{"s":"TRXUSDT","c":"web_st_Ihlt5wPQEpiqt1j","S":"SELL","o":"MARKET","f":"GTC","q":"150","p":"0","ap":"0","sp":"0","x":"NEW","X":"NEW","i":4014170256,"l":"0","z":"0","L":"0","T":1622812021756,"t":0,"b":"0","a":"0","m":"false","R":"false","wt":"CONTRACT_PRICE","ot":"MARKET","ps":"BOTH","cp":"false","rp":"0","pP":"false","si":25304722,"ss":1,"st":"OTOCO"}}

d1 = {"e":"ACCOUNT_UPDATE",
      "T":1622812021756,
      "E":1622812021758,
      "a":{"B":[{"a":"USDT",
                 "wb":"316.19421294",
                 "cw":"304.83274584",
                 "bc":"0"}],
           "P":[{"s":"TRXUSDT",
                 "pa":"-150",
                 "ep":"0.07574",
                 "cr":"25.89322001",
                 "up":"-0.00501150",
                 "mt":"isolated",
                 "iw":"11.36146710",
                 "ps":"BOTH",
                 "ma":"USDT"}],
           "m":"ORDER"}}


d2 = {"e":"ACCOUNT_UPDATE",
      "T":1622812118021,
      "E":1622812118026,
      "a":{"B":[{"a":"USDT",
                 "wb":"316.15065294",
                 "cw":"316.15065294",
                 "bc":"0"}],
           "P":[{"s":"TRXUSDT",
                 "pa":"0",
                 "ep":"0.00000",
                 "cr":"25.85422001",
                 "up":"0",
                 "mt":"isolated",
                 "iw":"0",
                 "ps":"BOTH",
                 "ma":"USDT"}],
           "m":"ORDER"}}







# for k, v in d1.items():
#     print(k, " : ", v)



"""


{
  "e": "ACCOUNT_UPDATE",                // Event Type
  "E": 1564745798939,                   // Event Time
  "T": 1564745798938 ,                  // Transaction
  "a":                                  // Update Data
    {
      "m":"ORDER",                      // Event reason type
      "B":[                             // Balances
        {
          "a":"USDT",                   // Asset
          "wb":"122624.12345678",       // Wallet Balance
          "cw":"100.12345678",          // Cross Wallet Balance
          "bc":"50.12345678"            // Balance Change except PnL and Commission
        },
        {
          "a":"BUSD",           
          "wb":"1.00000000",
          "cw":"0.00000000",         
          "bc":"-49.12345678"
        }
      ],
      "P":[
        {
          "s":"BTCUSDT",            // Symbol
          "pa":"0",                 // Position Amount
          "ep":"0.00000",            // Entry Price
          "cr":"200",               // (Pre-fee) Accumulated Realized
          "up":"0",                     // Unrealized PnL
          "mt":"isolated",              // Margin Type
          "iw":"0.00000000",            // Isolated Wallet (if isolated position)
          "ps":"BOTH"                   // Position Side
        }，
        {
            "s":"BTCUSDT",
            "pa":"20",
            "ep":"6563.66500",
            "cr":"0",
            "up":"2850.21200",
            "mt":"isolated",
            "iw":"13200.70726908",
            "ps":"LONG"
         },
        {
            "s":"BTCUSDT",
            "pa":"-10",
            "ep":"6563.86000",
            "cr":"-45.04000000",
            "up":"-1423.15600",
            "mt":"isolated",
            "iw":"6570.42511771",
            "ps":"SHORT"
        }
      ]
    }
}

"""











