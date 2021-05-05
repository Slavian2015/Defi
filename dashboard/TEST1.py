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
import dbrools
import Settings


main_path_data = os.path.expanduser('/usr/local/WB/data/')
warnings.filterwarnings("ignore")


api_key = Settings.API_KEY
api_secret = Settings.API_SECRET

bclient = Client(api_key=api_key, api_secret=api_secret)

"""
My History Trades
"""
# trades = bclient.get_my_trades(symbol='BNBUSDT', limit=10)
# print(trades)

# d = [{'symbol': 'ZECUSDT', 'id': 30787619, 'orderId': 705859683, 'orderListId': -1, 'price': '249.09000000', 'qty': '0.06000000',
#       'quoteQty': '14.94540000', 'commission': '0.00002127', 'commissionAsset': 'BNB', 'time': 1618824859035, 'isBuyer': True, 'isMaker': False, 'isBestMatch': True},
#      {'symbol': 'ZECUSDT', 'id': 30787741, 'orderId': 705863338, 'orderListId': -1, 'price': '249.59000000', 'qty': '0.06000000', 'quoteQty': '14.97540000',
#       'commission': '0.00002127', 'commissionAsset': 'BNB', 'time': 1618824936020, 'isBuyer': False, 'isMaker': False, 'isBestMatch': True},
#      {'symbol': 'ZECUSDT', 'id': 32788802, 'orderId': 741085556, 'orderListId': -1, 'price': '231.11000000', 'qty': '0.04327000', 'quoteQty': '10.00012970',
#       'commission': '0.00001258', 'commissionAsset': 'BNB', 'time': 1619707094021, 'isBuyer': True, 'isMaker': True, 'isBestMatch': True},
#
#      {'symbol': 'ZECUSDT', 'id': 32789229, 'orderId': 741099409, 'orderListId': -1, 'price': '231.68000000', 'qty': '0.38846000', 'quoteQty': '89.99841280',
#       'commission': '0.00011275', 'commissionAsset': 'BNB', 'time': 1619707512708, 'isBuyer': True, 'isMaker': True, 'isBestMatch': True}]
#
# for k, v in d[-1].items():
#     print(k, "  | ", v)


"""
My Open Orders
"""
# trades = bclient.get_open_orders()
# print(trades)
# d = [{'symbol': 'BNBUSDT', 'orderId': 2058247884, 'orderListId': -1, 'clientOrderId': 'web_6ecb53275f1c4521b2fab2c94ef34df6',
#       'price': '600.00000000', 'origQty': '0.02500000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000',
#       'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000',
#       'time': 1619778117516, 'updateTime': 1619778117516, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}]

# trades = bclient.get_all_orders(symbol='XRPUSDT', limit=10)
# print(trades)

"""
New Order
"""

# order = bclient.order_limit_buy(
#                     symbol='BNBUSDT',
#                     quantity='0.025',
#                     price=str(600))
#
# print(order)
#
# d = {'symbol': 'BNBUSDT',
#      'orderId': 2058335436,
#      'orderListId': -1,
#      'clientOrderId': 'MInemzvhvqWzJlPczpDERm',
#      'transactTime': 1619779149725,
#      'price': '600.00000000',
#      'origQty': '0.02500000',
#      'executedQty': '0.00000000',
#      'cummulativeQuoteQty': '0.00000000',
#      'status': 'NEW',
#      'timeInForce': 'GTC',
#      'type': 'LIMIT',
#      'side': 'BUY',
#      'fills': []}


"""
GET ALL ORDERS
"""

# orders = bclient.get_all_orders(symbol='BNBUSDT', limit=10)
# print(orders)
# d = [{'symbol': 'BNBUSDT',
#       'orderId': 2058335436,
#       'orderListId': -1,
#       'clientOrderId': 'MInemzvhvqWzJlPczpDERm',
#       'price': '600.00000000',
#       'origQty': '0.02500000',
#       'executedQty': '0.00000000',
#       'cummulativeQuoteQty': '0.00000000',
#       'status': 'NEW',
#       'timeInForce': 'GTC',
#       'type': 'LIMIT',
#       'side': 'BUY',
#       'stopPrice': '0.00000000',
#       'icebergQty': '0.00000000',
#       'time': 1619779149725,
#       'updateTime': 1619779149725,
#       'isWorking': True,
#       'origQuoteOrderQty': '0.00000000'}]


"""
Check order status
"""

# order = bclient.get_order(
#     symbol='BNBUSDT',
#     orderId=2058335436)
#
# print(order)
#
# d = {'symbol': 'BNBUSDT',
#      'orderId': 2058335436,
#      'orderListId': -1,
#      'clientOrderId': 'MInemzvhvqWzJlPczpDERm',
#      'price': '600.00000000',
#      'origQty': '0.02500000',
#      'executedQty': '0.00000000',
#      'cummulativeQuoteQty': '0.00000000',
#      'status': 'NEW',    # ....  'FILLED'   | 'CANCELED'  | 'PARTIALLY_FILLED'
#      'timeInForce': 'GTC',
#      'type': 'LIMIT',
#      'side': 'BUY',
#      'stopPrice': '0.00000000',
#      'icebergQty': '0.00000000',
#      'time': 1619779149725,
#      'updateTime': 1619779149725,
#      'isWorking': True,
#      'origQuoteOrderQty': '0.00000000'}



"""
GET ALL ORDERS 2  <<<<
"""
# orders = bclient.get_open_orders()
# print(orders)
#
# d = [{'symbol': 'BNBUSDT',
#       'orderId': 2058335436,
#       'orderListId': -1,
#       'clientOrderId': 'MInemzvhvqWzJlPczpDERm',
#       'price': '600.00000000',
#       'origQty': '0.02500000',
#       'executedQty': '0.00000000',
#       'cummulativeQuoteQty': '0.00000000',
#       'status': 'NEW',
#       'timeInForce': 'GTC',
#       'type': 'LIMIT',
#       'side': 'BUY',
#       'stopPrice': '0.00000000',
#       'icebergQty': '0.00000000',
#       'time': 1619779149725,
#       'updateTime': 1619779149725,
#       'isWorking': True,
#       'origQuoteOrderQty': '0.00000000'},
#
#      {'symbol': 'FILUSDT', 'orderId': 569033964, 'orderListId': -1,
#       'clientOrderId': 'web_dc97f9b3fed84b6c8ae2d4240d11396f', 'price': '140.00000000', 'origQty': '0.10710000',
#       'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC',
#       'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1619779769032,
#       'updateTime': 1619779769032, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}]


dd = [{'error': False,
       'result': {'symbol': 'YFIUPUSDT',
                  'orderId': 98339030,
                  'orderListId': -1,
                  'clientOrderId': 'e15d2V6dAYPxDvsk9yQyNq',
                  'transactTime': 1619704808279,
                  'price': '0.00000000',
                  'origQty': '16.26000000',
                  'executedQty': '16.26000000',
                  'cummulativeQuoteQty': '98.82828000',
                  'status': 'FILLED',
                  'timeInForce': 'GTC',
                  'type': 'MARKET',
                  'side': 'SELL',
                  'fills': [{'price': '6.07800000',
                             'qty': '16.26000000',
                             'commission': '0.00012410',
                             'commissionAsset': 'BNB',
                             'tradeId': 3316730}]}}]


for k,v in dd[0]:
    print(k, v)