# -*- coding: utf-8 -*-
import base64
import os
import sys

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import dbrools

sys.path.insert(0, r'/usr/local/WB')
main_path_data = os.path.expanduser('/usr/local/WB/dashboard/assets/')
main_path_data2 = os.path.expanduser('/usr/local/WB/data/')

symbols = ["XRP", "BTC", "ETH", "USDT",
           "TRX", "EOS", "BNB",
           "LINK", "FIL", "YFI",
           "DOT", "SXP", "UNI",
           "LTC", "ADA", "AAVE"]


def my_view():
    layout = [
        html.Div(
            style={
                "height": "100vh",
                "minHeight": "100vh",
                "maxHeight": "100vh",
                "overflowY": "hidden"
            },
            children=content())]
    return layout


def content():
    encoded_image = base64.b64encode(open(main_path_data + 'UserW.png', 'rb').read()).decode('ascii')

    balance_full = dbrools.get_my_balances()

    if balance_full:
        balance = "{0:.2f}$".format(float(balance_full["USDT"]))
    else:
        balance = "0"

    cont = [
        dbc.Row(style={"width": "100%",
                       "height": "10vh",
                       "minHeight": "10vh",
                       "maxHeight": "10vh",
                       "overflowY": "hidden",
                       "margin": "0",
                       "padding": "0"},
                children=[
                    dbc.Col(style={"textAlign": "center",
                                   "margin": "0",
                                   "padding": "0"
                                   },
                            width=5,
                            children=[
                                dbc.Row(style={"width": "100%",
                                               "margin": "0",
                                               "padding": "0"},
                                        children=[

                                            dbc.Col(style={"textAlign": "center",
                                                           "margin": "0",
                                                           "padding": "0"
                                                           },
                                                    width=4,
                                                    children=[
                                                        dbc.Button("BALANCE", id="balance_btn", color="warning")])
                                        ])]),
                    dbc.Col(style={"textAlign": "center",
                                   "margin": "0",
                                   "padding": "0"
                                   },
                            children=[html.Div()]),
                    dbc.Col(style={"textAlign": "center",
                                   "margin": "0",
                                   "padding": "0"
                                   },
                            width=5,
                            children=dbc.Row(style={"width": "100%",
                                                    "margin": "0",
                                                    "padding": "0"},
                                             children=[
                                                 dbc.Col(style={"textAlign": "center",
                                                                "margin": "0",
                                                                "padding": "0"
                                                                },
                                                         children=[
                                                             html.H3(balance,
                                                                     id="usdt_balance",
                                                                     style={"textAlign": "center",
                                                                            "margin": "0",
                                                                            "padding": "0"
                                                                            })
                                                         ]),
                                             ])
                            ),
                ],
                no_gutters=True
                ),

        dbc.Row(style={"width": "100%",
                       "height": "89vh",
                       "minHeight": "89vh",
                       "maxHeight": "89vh",
                       "overflowY": "scroll",
                       "margin": "0",
                       "padding": "0"},
                children=[
                    dbc.Col(style={"textAlign": "center",
                                   "maxHeight": "70vh",
                                   "overflowY": "scroll",
                                   "margin": "0",
                                   "padding": "0"
                                   },
                            width=8,
                            sm=12,
                            lg=8,
                            xs=12,
                            className="no-scrollbars",
                            children=dbc.Row(style={"width": "100%",
                                                    "margin": "0",
                                                    "padding": "0"},
                                             id="new_trade_history",
                                             className="no-scrollbars",
                                             children=trade_history())),
                    dbc.Col(style={"textAlign": "center",
                                   "height": "89vh",
                                   "minHeight": "89vh",
                                   "maxHeight": "89vh",
                                   "overflowY": "scroll",
                                   "margin": "0",
                                   "padding": "0"},
                            className="no-scrollbars",
                            width=4,
                            sm=12,
                            lg=4,
                            xs=12,
                            children=column_right()),
                ],
                no_gutters=True)]

    return cont


def column_left():
    form = dbc.Form(
        [
            dbc.FormGroup(
                [
                    dbc.Label("API_key", className="mr-2"),
                    dbc.Input(type="password", id="example-api-key_bin", placeholder="Enter API-key"),
                ],
                className="mr-3",
            ),
            dbc.FormGroup(
                [
                    dbc.Label("API_secret", className="mr-2"),
                    dbc.Input(type="password", id="example-api-secret_bin", placeholder="Enter API-secret"),
                ],
                className="mr-3",
            ),
            dbc.Button("Сохранить Binance", id="save_api_bin", color="primary"),
            dbc.Toast(
                [html.P("Done !")],
                id="save_api_bin_toast",
                is_open=False,
                icon="info",
                style={"position": "fixed", "top": 200, "right": 1200, "width": 250},
                duration=2000,
            ),
        ],
        inline=True,
    )

    form2 = dbc.Form(
        [
            dbc.FormGroup(
                [
                    dbc.Label("API_key", className="mr-2"),
                    dbc.Input(type="password", id="example-api-key_telega", placeholder="Enter API-key"),
                ],
                className="mr-3",
            ),
            dbc.FormGroup(
                [
                    dbc.Label("API_secret", className="mr-2"),
                    dbc.Input(type="password", id="example-api-secret_telega", placeholder="example.: 494797976"),
                ],
                className="mr-3",
            ),
            dbc.Button("Сохранить Telegram", id="save_api_telega", color="primary"),
            dbc.Toast(
                [html.P("Done !")],
                id="save_api_telega_toast",
                is_open=False,
                icon="info",
                style={"position": "fixed", "top": 200, "right": 1200, "width": 250},
                duration=2000,
            ),
        ],
        inline=True,
    )

    cont = [
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       "margin-bottom": "5px",
                       "padding": "0"},
                no_gutters=False,
                children=form),
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       "margin-bottom": "50px",
                       "padding": "0"},
                no_gutters=False,
                children=form2),
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       "padding": "0"},
                justify="center",
                align="center",
                id="new_left_side",
                no_gutters=False,
                children=sub_column_left()),
    ]

    return cont


def sub_column_left():
    data = dbrools.get_active_data()

    cards = []
    for k, v in enumerate(data):
        if v["side"] != "sell":
            my_img = html.Img(style={"padding": "0",
                                     "margin": "0",
                                     "max_height": "25px",
                                     "max-width": "25px"
                                     },
                              src='data:image/png;base64,{}'.format(
                                  base64.b64encode(open(main_path_data + f'{v["symbol"]}.png', 'rb').read()).decode(
                                      'ascii')))

            if v["process"] == 0:
                my_button = "START"
                my_button_color = "success"
            else:
                my_button = "STOP"
                my_button_color = "danger"

            row = dbc.Row(style={"margin": "0", "padding": "0"},
                          children=[
                              dbc.Col(width=3, lg=3, children=[
                                  my_img
                              ]),

                              dbc.Col(width=3, lg=3, children=[
                                  html.H5(v["symbol"],
                                          id={"type": "symbol_name", "index": k}
                                          )
                              ]),

                              dbc.Col(width=3, lg=3, children=[
                                  dbc.Input(type="number",
                                            id={"type": "symbol_amount", "index": k},
                                            value=float(v["amount"])
                                            ),
                              ]),

                              dbc.Col(width=3, lg=3, children=[
                                  dbc.Button(my_button,
                                             id={"type": "symbol_button", "index": k},
                                             color=my_button_color),
                              ]),
                          ])
            cards.append(row)

    return cards


def column_right():
    interval = dcc.Interval(id='interval_price', interval=5000, n_intervals=0)
    cont = [
        interval,
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       # "height": "28vh",
                       # "minHeight": "28vh",
                       "maxHeight": "28vh",
                       "overflowY": "scroll",
                       "padding": "0"},
                id="my_wallet_balance",
                children=my_wallet()),
        dbc.Row(style={"width": "100%",
                       "height": "5vh",
                       "minHeight": "5vh",
                       "maxHeight": "5vh",
                       "overflowY": "hidden",
                       "padding": "0"},
                children=[]),
        dbc.Row(style={"width": "100%",
                       "height": "60vh",
                       "minHeight": "60vh",
                       "maxHeight": "60vh",
                       "overflowY": "scroll",
                       "margin": "0",
                       "padding": "0"},
                className="no-scrollbars",
                children=column_left()),
    ]

    return cont


def my_wallet():
    pic_cards = []
    balances = dbrools.get_my_balances()

    if balances:
        for k, v in balances.items():
            if k not in ["_id", "sku"]:
                if float(v) > 0:
                    if k in symbols:
                        my_img = html.Img(style={"padding": "0",
                                                 "margin": "0",
                                                 "max_height": "20px",
                                                 "max-width": "20px"},
                                          src='data:image/png;base64,{}'.format(
                                              base64.b64encode(open(main_path_data + f'{k}.png', 'rb').read()).decode(
                                                  'ascii')))
                    else:
                        my_img = []
                    my_col = dbc.Button(children=dbc.Row(style={"width": "100%",
                                                                "margin": "0",
                                                                "padding": "0"},
                                                         className="no-scrollbars",
                                                         children=[
                                                             dbc.Col(style={"textAlign": "left",
                                                                            "margin": "0",
                                                                            "padding": "0"},
                                                                     width=1,
                                                                     children=my_img),
                                                             dbc.Col(style={"textAlign": "right",
                                                                            "margin": "0",
                                                                            "padding": "0"},
                                                                     width=4,
                                                                     children=k.upper()),
                                                             dbc.Col(style={"textAlign": "center",
                                                                            "margin": "0",
                                                                            "padding": "0"},
                                                                     width=7,
                                                                     children=html.P("{0:.3f}".format(float(v)),
                                                                                     style={"color": "white",
                                                                                            "margin": "0",
                                                                                            "padding": "0"
                                                                                            }))
                                                         ]),
                                        style={"min-width": "150px",
                                               "max-width": "150px",
                                               # "min-height": "50px",
                                               # "max-height": "50px",
                                               "margin": "1px",
                                               # "padding": "0"
                                               },
                                        outline=True,
                                        color="info")
                    pic_cards.append(my_col)

    return pic_cards


def trade_history():
    table_header = [
        html.Thead(html.Tr(
            [
                html.Th(""),
                html.Th("Amount"),
                html.Th("Price"),
                html.Th("Direction"),
                html.Th("Date"),
            ],
            style={"font-size": "15px", "textAlign": "center"}))
    ]

    table_body = [html.Tbody(my_trade_history(),
                             id="trade_table")]

    table = dbc.Table(table_header + table_body,
                      style={"width": "100%", 'border-collapse': 'collapse'},
                      className="no-scrollbars",
                      bordered=True,
                      hover=True,
                      # dark=True,
                      responsive=True,
                      striped=True)
    return table


def my_trade_history():
    my_list = []

    items = dbrools.get_history_data()
    if not items:
        items = [
            {
                "symbol": "LTC",
                "amount": "0.33",
                "price": '165',
                "direct": 'SELL',
                "date": '21.02.2021'
            },
            {
                "symbol": "BTC",
                "amount": "1.4533",
                "price": '43005',
                "direct": 'BUY',
                "date": '17.02.2021'
            },
            {
                "symbol": "BNB",
                "amount": "5648",
                "price": '165',
                "direct": 'SELL',
                "date": '22.02.2021'
            },
            {
                "symbol": "LTC",
                "amount": "0.33",
                "price": '165',
                "direct": 'BUY',
                "date": '21.02.2021'
            },
        ]

    for v in reversed(items):
        try:
            if v["result"] == 1:
                new_color = "red"
            elif v["result"] == 2:
                new_color = "green"
            else:
                new_color = 'transparent'
        except KeyError:
            new_color = 'transparent'

        child = html.Tr([
            html.Th([html.P(v["symbol"], style={"min-width": "70px"})], style={"padding": "0", "margin": "0"}),
            html.Th([html.P("{0:.6f}".format(float(v["amount"])), style={"min-width": "70px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([html.P("{0:.6f}".format(float(v["price"])), style={"min-width": "70px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([dbc.Badge(v["direct"], style={"min-width": "70px"},
                               color="success" if v["direct"] == "BUY" else "danger")],
                    style={"padding": "0", "margin": "0"}),
            html.Th([html.P(v["date"], style={"min-width": "70px"})], style={"padding": "0", "margin": "0"}),
        ], style={"background-color": new_color})

        my_list.append(child)

    return my_list
