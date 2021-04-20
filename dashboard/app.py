import dash, json, sys, os
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH, ALL
import flask
import layouts, grafs_layout
import Orders
import subprocess
import threading
import warnings
import dbrools
from datetime import datetime

warnings.filterwarnings("ignore")

main_path_data = os.path.expanduser('/usr/local/WB/data')


def output_reader(proc, file):
    while True:
        byte = proc.stdout.read(1)
        if byte:
            sys.stdout.buffer.write(byte)
            sys.stdout.flush()
            file.buffer.write(byte)
        else:
            break


external_stylesheets = [dbc.themes.DARKLY]
app = flask.Flask(__name__)
dash_app = dash.Dash(__name__,
                     url_base_pathname="/",
                     server=app,
                     external_stylesheets=external_stylesheets,
                     meta_tags=[
                         {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                     ])
dash_app.title = 'DeFi'

dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div("TEST", id="hidden_port", style={'display': 'none'})
])


@dash_app.callback(Output('page-content', 'children'),
                   [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return layouts.my_view()
    elif pathname == '/all':
        return grafs_layout.my_view()
    else:
        return "404"


# ###############################    REGIM BUTTONS    ##################################
@dash_app.callback([Output('hidden_port', 'children')],
                   [Input('kline_on', 'n_clicks'),
                    Input('kline_off', 'n_clicks'),
                    ])
def trigger_by_modify(n1, n2):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')
    # print(button_id[0])
    # if n1 == 0 and n2 == 0 and n3 == 0 and n4 == 0 and n5 == 0 and n6 == 0:
    #     raise PreventUpdate
    # if button_id[0] == 'parser_on':
    #     a_file1 = open(main_path_data + "/bal.json", "r")
    #     rools = json.load(a_file1)
    #     a_file1.close()
    #     if rools["bin"] == 5000:
    #         rools["bin"] = 1000
    #     else:
    #         rools["bin"] = 5000
    #
    #     f = open(main_path_data + "/bal.json", "w")
    #     json.dump(rools, f)
    #     f.close()
    #
    #     # with subprocess.Popen(["python", '/usr/local/WB/dashboard/My_parser.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc1, \
    #     #         open('/usr/local/WB/data/Parser_Main.log', 'w') as file1:
    #     #     t1 = threading.Thread(target=output_reader, args=(proc1, file1))
    #     #     t1.start()
    #     #     t1.join()
    #     return [layouts.start_buttons_card(b1=True, b2=False, b3=False, b4=False)]
    # # elif button_id[0] == 'parser_off':
    # #     # script = "/usr/local/WB/dashboard/My_parser.py"
    # #     # subprocess.check_call(["pkill", "-9", "-f", script])
    # #     return [layouts.start_buttons_card(b1=False, b2=True, b3=False, b4=False)]
    if button_id[0] == 'kline_on' and n1 > 0:
        with subprocess.Popen(["python", '/usr/local/WB/dashboard/PARSER_kline.py'], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as proc1, \
                open('/usr/local/WB/data/my_logs/kline_log.txt', 'w') as file1:
            t1 = threading.Thread(target=output_reader, args=(proc1, file1))
            t1.start()
            t1.join()
        return ["kline_on"]
    elif button_id[0] == 'kline_off':
        script = "/usr/local/WB/dashboard/PARSER_kline.py"
        subprocess.check_call(["pkill", "-9", "-f", script])
        return ["kline_off"]
    else:
        raise PreventUpdate


# ###############################    REFRESH BALANCE    ##################################
@dash_app.callback([Output('usdt_balance', 'children')],
                   [Input('balance_btn', 'n_clicks')])
def trigger_balance(n1):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')
    if button_id[0] == 'balance_btn':
        Orders.my_balance()
        repons = dbrools.get_my_balances()

        return ["{0:.2f} $".format(float(repons['USDT']))]
    else:
        raise PreventUpdate


# ###############################    SELECT GRAFS MAIN    ##################################
@dash_app.callback(
    [Output('my_wallet_balance', 'children')],
    [Input("interval_price", 'n_intervals')])
def trigger_by_modify(n1):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')

    if button_id[0] == 'interval_price':
        card = layouts.my_wallet()
        return [card]
    else:
        raise PreventUpdate

#
# # ###############################    Refresh GRAFS ALL    ##################################
# @dash_app.callback(
#     [Output('graf_long', 'children'),
#      Output('graf_short', 'children'),
#      ],
#     [Input("interval_graf_long_short", 'n_intervals')])
# def trigger_by_modify(n1):
#     ctx = dash.callback_context
#     button_id = ctx.triggered[0]['prop_id'].split('.')
#
#     if button_id[0] == 'interval_graf_long_short':
#         row1, row2 = grafs_layout.columns()
#         return row1, row2
#     else:
#         raise PreventUpdate
#
#
# # ##############################   Orders   ##################################
# @dash_app.callback(
#     [Output({'type': 'order_result', 'index': MATCH}, "children")],
#
#     [Input({'type': 'order_buy_btn', 'index': MATCH}, 'n_clicks'),
#      Input({'type': 'order_sell_btn', 'index': MATCH}, 'n_clicks'),
#      Input({'type': 'order_sec_btn', 'index': MATCH}, 'value'),
#      Input({'type': 'order_qty_btn', 'index': MATCH}, 'value'),
#      Input({'type': 'order_price_btn', 'index': MATCH}, 'value')],
#
#     [State({'type': 'order_sec_btn', 'index': MATCH}, 'value'),
#      State({'type': 'order_price_btn', 'index': MATCH}, 'value'),
#      State({'type': 'order_qty_btn', 'index': MATCH}, 'value')]
# )
# def toggle_modal(n1, n2, n3, n4, n5, symbol, price, qty):
#     trigger = dash.callback_context.triggered[0]
#     button = trigger["prop_id"].split(".")[0]
#     symbols = ["LTCUPUSDT", "ETHUPUSDT", "BTCUPUSDT", "BNBUPUSDT"]
#     if not button:
#         raise PreventUpdate
#     else:
#         if type(button) is str:
#             button = json.loads(button.replace("'", "\""))
#         if button["type"] == 'order_sec_btn':
#             if symbol in symbols:
#                 prices = dbrools.get_my_data()
#                 b1 = "{0:.2f}".format(float(prices["data"]['LTCUPUSDT']['asks']))
#                 b2 = "{0:.2f}".format(float(prices["data"]['LTCUPUSDT']['bids']))
#                 return [f"ask: {b1} / bid: {b2}"]
#             else:
#                 raise PreventUpdate
#         elif button["type"] == 'order_price_btn':
#             if price is not None and qty is not None:
#                 result = float(price) * float(qty)
#                 return [f"{result} $"]
#             else:
#                 raise PreventUpdate
#         elif button["type"] == 'order_qty_btn':
#             if symbol in symbols and qty is not None:
#                 # my_new_price = dbrools.get_my_data()
#                 # result = float(my_new_price["data"][symbol]["a"][-1]) * float(qty)
#                 return [None]
#             else:
#                 raise PreventUpdate
#         elif button["type"] == 'order_buy_btn':
#             if not symbol or not qty:
#                 return ["ERROR"]
#             reponse = Orders.my_order(symbol=symbol, side=1, amount=qty, price=price)
#             if reponse["error"]:
#                 return [f"{reponse['result']}"]
#             prices = dbrools.get_my_data()
#             b1 = "{0:.2f}".format(float(prices["data"][symbol]['asks']))
#             data = {
#                 "symbol": symbol[0:3],
#                 "amount": qty,
#                 "price": b1,
#                 "direct": 'BUY',
#                 "date": f"{datetime.now().strftime('%d.%m.%Y')}"
#             }
#             dbrools.add_my_history(data=data)
#             return [f"You bought {symbol}"]
#         elif button["type"] == 'order_sell_btn':
#             if not symbol or not qty:
#                 return ["ERROR"]
#             reponse = Orders.my_order(symbol=symbol, side=2, amount=qty, price=price)
#             if reponse["error"]:
#                 return [f"{reponse['result']}"]
#
#             prices = dbrools.get_my_data()
#             b1 = "{0:.2f}".format(float(prices["data"][symbol]['bids']))
#
#             data = {
#                 "symbol": symbol[0:3],
#                 "amount": qty,
#                 "price": b1,
#                 "direct": 'SELL',
#                 "date": f"{datetime.now().strftime('%d.%m.%Y')}"
#             }
#             dbrools.add_my_history(data=data)
#
#             return [f"You sold {symbol}"]
#         else:
#             raise PreventUpdate
#
#
# # ##############################   SHOW REPONSE   ##################################
# @dash_app.callback(
#     [Output("auto_toast", "is_open"),
#      Output("auto_toast", "children"),
#      Output("trade_table", "children")],
#     [Input("ltc_buy", "n_clicks"),
#      Input("ltc_sell", "n_clicks"),
#      Input("eth_buy", "n_clicks"),
#      Input("eth_sell", "n_clicks"),
#      Input("btc_buy", "n_clicks"),
#      Input("btc_sell", "n_clicks"),
#      Input("bnb_buy", "n_clicks"),
#      Input("bnb_sell", "n_clicks")],
#     [State("ltc_qty", "value"),
#      State("eth_qty", "value"),
#      State("btc_qty", "value"),
#      State("bnb_qty", "value")],
# )
# def open_toast(n1, n2, n3, n4, n5, n6, n7, n8, s1, s2, s3, s4):
#
#     ctx = dash.callback_context
#     button_id = ctx.triggered[0]['prop_id'].split('.')
#
#     if button_id[0] == 'ltc_buy':
#         prices = dbrools.get_my_data()
#         b1 = float(prices["data"]['LTCUPUSDT']['asks'])
#         qty = float(s1)/b1
#
#         reponse = Orders.my_order(symbol="LTCUPUSDT", side=1, amount=qty, price=None)
#         if reponse["error"]:
#             return True, [f"{reponse['result']}"]
#
#         data = {
#             "symbol": "LTC",
#             "amount": qty,
#             "price": b1,
#             "direct": 'BUY',
#             "date": f"{datetime.now().strftime('%d.%m.%Y')}"
#         }
#         dbrools.add_my_history(data=data)
#
#         d = html.P(f"YOU bought (LTCUP), qty: {qty}", className="mb-0")
#         return True, d, layouts.my_trade_history()
#     elif button_id[0] == 'ltc_sell':
#
#         prices = dbrools.get_my_data()
#         balance = dbrools.get_my_balances()["LTCUP"]
#
#         b1 = float(prices["data"]['LTCUPUSDT']['bids'])
#
#         reponse = Orders.my_order(symbol="LTCUPUSDT", side=2, amount=balance, price=None)
#         if reponse["error"]:
#             return True, [f"{reponse['result']}"]
#
#         data = {
#             "symbol": "LTC",
#             "amount": balance,
#             "price": b1,
#             "direct": 'SELL',
#             "date": f"{datetime.now().strftime('%d.%m.%Y')}"
#         }
#         dbrools.add_my_history(data=data)
#
#         d = html.P(f"YOU sold (LTCUP), qty: {balance}", className="mb-0")
#         return True, d, layouts.my_trade_history()
#     elif button_id[0] == 'eth_buy':
#         prices = dbrools.get_my_data()
#         b1 = float(prices["data"]['ETHUPUSDT']['asks'])
#         qty = float(s2)/b1
#
#         reponse = Orders.my_order(symbol="ETHUPUSDT", side=1, amount=qty, price=None)
#         if reponse["error"]:
#             return True, [f"{reponse['result']}"]
#
#         data = {
#             "symbol": "ETH",
#             "amount": qty,
#             "price": b1,
#             "direct": 'BUY',
#             "date": f"{datetime.now().strftime('%d.%m.%Y')}"
#         }
#         dbrools.add_my_history(data=data)
#
#         d = html.P(f"YOU bought (ETHUP), qty: {qty}", className="mb-0")
#         return True, d, layouts.my_trade_history()
#     elif button_id[0] == 'eth_sell':
#
#         prices = dbrools.get_my_data()
#         balance = dbrools.get_my_balances()["ETHUP"]
#
#         b1 = float(prices["data"]['ETHUPUSDT']['bids'])
#
#         reponse = Orders.my_order(symbol="ETHUPUSDT", side=2, amount=balance, price=None)
#         if reponse["error"]:
#             return True, [f"{reponse['result']}"]
#
#         data = {
#             "symbol": "ETH",
#             "amount": balance,
#             "price": b1,
#             "direct": 'SELL',
#             "date": f"{datetime.now().strftime('%d.%m.%Y')}"
#         }
#         dbrools.add_my_history(data=data)
#
#         d = html.P(f"YOU sold (ETHUP), qty: {balance}", className="mb-0")
#         return True, d, layouts.my_trade_history()
#     elif button_id[0] == 'btc_buy':
#         prices = dbrools.get_my_data()
#         b1 = float(prices["data"]['BTCUPUSDT']['asks'])
#         qty = float(s3)/b1
#
#         reponse = Orders.my_order(symbol="BTCUPUSDT", side=1, amount=qty, price=None)
#         if reponse["error"]:
#             return True, [f"{reponse['result']}"]
#
#         data = {
#             "symbol": "BTC",
#             "amount": qty,
#             "price": b1,
#             "direct": 'BUY',
#             "date": f"{datetime.now().strftime('%d.%m.%Y')}"
#         }
#         dbrools.add_my_history(data=data)
#
#         d = html.P(f"YOU bought (BTCUP), qty: {qty}", className="mb-0")
#         return True, d, layouts.my_trade_history()
#     elif button_id[0] == 'btc_sell':
#
#         prices = dbrools.get_my_data()
#         balance = dbrools.get_my_balances()["BTCUP"]
#
#         b1 = float(prices["data"]['BTCUPUSDT']['bids'])
#
#         reponse = Orders.my_order(symbol="BTCUPUSDT", side=2, amount=balance, price=None)
#         if reponse["error"]:
#             return True, [f"{reponse['result']}"]
#
#         data = {
#             "symbol": "BTC",
#             "amount": balance,
#             "price": b1,
#             "direct": 'SELL',
#             "date": f"{datetime.now().strftime('%d.%m.%Y')}"
#         }
#         dbrools.add_my_history(data=data)
#
#         d = html.P(f"YOU sold (BTCUP), qty: {balance}", className="mb-0")
#         return True, d, layouts.my_trade_history()
#     elif button_id[0] == 'bnb_buy':
#         prices = dbrools.get_my_data()
#         b1 = float(prices["data"]['BNBUPUSDT']['asks'])
#         qty = float(s4)/b1
#
#         reponse = Orders.my_order(symbol="BNBUPUSDT", side=1, amount=qty, price=None)
#         if reponse["error"]:
#             return True, [f"{reponse['result']}"]
#
#         data = {
#             "symbol": "BNB",
#             "amount": qty,
#             "price": b1,
#             "direct": 'BUY',
#             "date": f"{datetime.now().strftime('%d.%m.%Y')}"
#         }
#         dbrools.add_my_history(data=data)
#
#         d = html.P(f"YOU bought (BNBUP), qty: {qty}", className="mb-0")
#         return True, d, layouts.my_trade_history()
#     elif button_id[0] == 'bnb_sell':
#
#         prices = dbrools.get_my_data()
#         balance = dbrools.get_my_balances()["BNBUP"]
#
#         b1 = float(prices["data"]['BNBUPUSDT']['bids'])
#
#         reponse = Orders.my_order(symbol="BNBUPUSDT", side=2, amount=balance, price=None)
#         if reponse["error"]:
#             return True, [f"{reponse['result']}"]
#
#         data = {
#             "symbol": "BNB",
#             "amount": balance,
#             "price": b1,
#             "direct": 'SELL',
#             "date": f"{datetime.now().strftime('%d.%m.%Y')}"
#         }
#         dbrools.add_my_history(data=data)
#
#         d = html.P(f"YOU sold (BNBUP), qty: {balance}", className="mb-0")
#         return True, d, layouts.my_trade_history()
#     else:
#         raise PreventUpdate


if __name__ == '__main__':
    dash_app.run_server(host="0.0.0.0", port=5033, debug=False)
