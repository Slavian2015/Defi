from binance.exceptions import BinanceAPIException, BinanceOrderException
import dbrools
import logging


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("BD")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


def my_order(client=None, symbol=None, side=None, amount=None, price=None):
    my_reponse = {"error": False, "result": None}
    try:
        if price:
            if side == 1:
                order = client.order_limit_buy(
                    symbol=symbol,
                    quantity=amount,
                    price=price)
            else:
                order = client.order_limit_sell(
                    symbol=symbol,
                    quantity=amount,
                    price=price)
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


def my_order_future(client=None, symbol=None, side=None, amount=None):
    my_reponse = {"error": False, "result": None}
    try:
        if side == 1:
            order = client.futures_create_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quantity=amount)
        else:
            order = client.futures_create_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=amount)
        my_reponse["result"] = order
    except BinanceOrderException as e:
        my_reponse["result"] = str(e)
        my_reponse["error"] = True
    except BinanceAPIException as e:
        my_reponse["result"] = str(e)
        my_reponse["error"] = True
    return my_reponse


def tp_future(client=None, symbol=None, side=None, price=None, amount=None):
    my_reponse = {"error": False, "result": None}
    try:
        if side == 1:
            order = client.futures_create_order(symbol=symbol,
                                                side='SELL',
                                                type='TAKE_PROFIT_MARKET',
                                                quantity=amount,
                                                reduceOnly='true',
                                                stopPrice=price)
        else:
            order = client.futures_create_order(symbol=symbol,
                                                side='BUY',
                                                type='TAKE_PROFIT_MARKET',
                                                quantity=amount,
                                                reduceOnly='true',
                                                stopPrice=price)
        my_reponse["result"] = order
    except BinanceOrderException as e:
        my_reponse["result"] = str(e)
        my_reponse["error"] = True
    except BinanceAPIException as e:
        my_reponse["result"] = str(e)
        my_reponse["error"] = True
    return my_reponse


def sl_future(client=None, symbol=None, side=None, price=None, amount=None):
    my_reponse = {"error": False, "result": None}
    try:
        if side == 1:
            order = client.futures_create_order(symbol=symbol,
                                                side='SELL',
                                                type='STOP_MARKET',
                                                reduceOnly='true',
                                                quantity=amount,
                                                stopPrice=price)
        else:
            order = client.futures_create_order(symbol=symbol,
                                                side='BUY',
                                                type='STOP_MARKET',
                                                reduceOnly='true',
                                                quantity=amount,
                                                stopPrice=price)
        my_reponse["result"] = order
    except BinanceOrderException as e:
        my_reponse["result"] = str(e)
        my_reponse["error"] = True
    except BinanceAPIException as e:
        my_reponse["result"] = str(e)
        my_reponse["error"] = True
    return my_reponse


def my_open_orders(client=None):
    my_reponse = {"error": False,
                  "result": None}

    try:
        my_orders = client.get_open_orders()
        my_reponse["result"] = my_orders
    except BinanceAPIException as e:
        my_reponse["result"] = e
        my_reponse["error"] = True

    return my_reponse


def my_balance(client=None):
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
            logging.error(f"(DEfi) BALANCE error:\n {str(e)}")

    my_reponse["error"] = True
    my_reponse["result"] = error
    return my_reponse
