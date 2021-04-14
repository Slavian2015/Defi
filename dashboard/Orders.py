import math
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import Settings, dbrools
import time, requests

telega_api_key = Settings.TELEGA_KEY
telega_api_secret = Settings.TELEGA_API

api_key = Settings.API_KEY
api_secret = Settings.API_SECRET
client = Client(api_key, api_secret)

symbols = ["XRP", "BTC", "ETH",
           "TRX", "EOS", "BNB",
           "LINK", "FIL", "YFI",
           "DOT", "SXP", "UNI",
           "LTC", "ADA", "AAVE"]
full_list = ['XRPUPUSDT', 'XRPDOWNUSDT', 'BTCUPUSDT', 'BTCDOWNUSDT', 'ETHUPUSDT', 'ETHDOWNUSDT',
             'TRXUPUSDT', 'TRXDOWNUSDT', 'EOSUPUSDT', 'EOSDOWNUSDT', 'BNBUPUSDT', 'BNBDOWNUSDT',
             'LINKUPUSDT', 'LINKDOWNUSDT', 'FILUPUSDT', 'FILDOWNUSDT', 'YFIUPUSDT', 'YFIDOWNUSDT',
             'DOTUPUSDT', 'DOTDOWNUSDT', 'SXPUPUSDT', 'SXPDOWNUSDT', 'UNIUPUSDT', 'UNIDOWNUSDT',
             'LTCUPUSDT', 'LTCDOWNUSDT', 'ADAUPUSDT', 'ADADOWNUSDT', 'AAVEUPUSDT', 'AAVEDOWNUSDT']


def my_order(symbol=None, side=None, amount=None, price=None):
    my_reponse = {"error": False, "result": None}
    try:
        if price:
            if side == 1:
                order = client.order_limit_buy(
                    symbol=symbol,
                    quantity=amount,
                    price=str(price))
            else:
                order = client.order_limit_sell(
                    symbol=symbol,
                    quantity=amount,
                    price=str(price))
        else:
            if side == 1:
                order = client.order_market_buy(
                    symbol=symbol,
                    quantity=amount)
            else:
                order = client.order_market_sell(
                    symbol=symbol,
                    quantity=amount)
        my_reponse["result"] = order
    except BinanceOrderException as e:
        my_reponse["result"] = str(e)
        my_reponse["error"] = True
    except BinanceAPIException as e:
        my_reponse["result"] = str(e)
        my_reponse["error"] = True
    return my_reponse


def my_open_orders():
    my_reponse = {"error": False,
                  "result": None}

    try:
        my_orders = client.get_open_orders()
        my_reponse["result"] = my_orders
    except BinanceAPIException as e:
        my_reponse["result"] = e
        my_reponse["error"] = True

    return my_reponse


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


#  ------------------------ ETHB ----------------------------

def bot_sendtext(bot_message):
    bot_token = telega_api_key
    bot_chat_id = telega_api_secret
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + bot_message
    requests.get(send_text)
    return


def my_balance():
    my_reponse = {"error": False,
                  "result": None}
    n = 0
    rep = True
    error = None

    sectors = ["USDT", "ETHUP"]

    while rep and n < 10:
        try:
            my_bal = client.get_account()

            now_list = []
            for i in my_bal["balances"]:
                dbrools.update_balances(i['asset'], i['free'])
                now_list.append(i['asset'])
            rep = False
            my_reponse["result"] = "ok"

            for i in sectors:
                if i not in now_list:
                    dbrools.update_balances(i, 0)
            return my_reponse

        except BinanceAPIException as e:
            n += 1
            error = e
            bot_sendtext(f"(BiBoT) BALANCE error:\n {str(e)}")

    my_reponse["error"] = True
    my_reponse["result"] = error
    return my_reponse