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

sys.path.insert(0, r'/usr/local/WB/dashboard')
import Settings

main_path_data = os.path.expanduser('/usr/local/WB/data/')
warnings.filterwarnings("ignore")

api_key = Settings.API_KEY
api_secret = Settings.API_SECRET
# testnet = True
bclient = Client(api_key=api_key, api_secret=api_secret, testnet=True)

"""
CHECK FUTURE BALANCE
"""
# my_bal = bclient.futures_account_balance()
#
# for i in my_bal:
#     print(i["asset"], " : ", i["balance"])


"""
CHANGE SYMBOL marginType (ISOLATED)
"""

# rep = bclient.futures_change_margin_type(symbol='SUSHIUSDT', marginType="ISOLATED")
# print(rep)


"""
CHECK FUTURE ACCOUNT
"""

# my_bal = bclient.futures_account()
#
# for i in my_bal['positions']:
#     print(i['symbol'], "leverage :", i['leverage'], "--------", "isolated: ", i['isolated'])


"""
CHANGE SYMBOL LEVERAGE
"""

# rep = bclient.futures_change_leverage(symbol='SUSHIUSDT', leverage=50)
# print(rep)

"""
FUTURE ORDER
    1) выставить ордер (зайти в позицию)
    2) выставить 2 ордера (стоп-лосс / тейк-профит) ---   reduceOnly='true'
    3) Отменить все открытые ордера
"""

# rep = bclient.futures_create_order(symbol='SUSHIUSDT', side='LONG', type='MARKET', quantity=100)
# rep = bclient.futures_create_order(symbol='SUSHIUSDT', side='SHORT', type='MARKET', quantity=100)
# print(rep)

rep2 = bclient.futures_create_order(symbol='BTCUSDT',
                                    side='BUY',
                                    type='MARKET',
                                    timeInForce='GTC',
                                    quantity=100)

print(rep2)

rep3 = bclient.futures_create_order(symbol='BTCUSDT',
                                    side='SELL',
                                    type='TAKE_PROFIT',
                                    # type='STOP/STOP_MARKET  or TAKE_PROFIT/TAKE_PROFIT_MARKET',
                                    timeInForce='GTC',
                                    reduceOnly='true',
                                    stopPrice=38000,
                                    closePosition='true',
                                    workingType="MARK_PRICE",
                                    priceProtect="TRUE")

print(rep3)
