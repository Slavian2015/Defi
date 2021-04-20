# -*- coding: utf-8 -*-
import json
import time

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import sys, base64, os
import plotly.graph_objects as go
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
    balance = "{0:.2f} $".format(float(balance_full["USDT"]))

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
                            width=4,
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
                                                        dbc.Button("BALANCE", id="balance_btn", color="warning")]),
                                            dbc.Col(style={"textAlign": "center",
                                                           "margin": "0",
                                                           "padding": "0"
                                                           },
                                                    width=4,
                                                    children=[
                                                        dbc.Button("GRAFS", href="/all", color="info")]),
                                            dbc.Col(style={"textAlign": "center",
                                                           "margin": "0",
                                                           "padding": "0"
                                                           },
                                                    width=4,
                                                    children=[
                                                        dbc.Button("ALERT", color="danger")]),
                                        ])]),
                    dbc.Col(style={"textAlign": "center",
                                   "margin": "0",
                                   "padding": "0"
                                   },
                            width=4,
                            children=[
                                dbc.ButtonGroup(
                                    [dbc.Button("ON1",
                                                id="kline_on",
                                                n_clicks=0,
                                                color="success"),
                                     dbc.Button("OFF",
                                                id="kline_off",
                                                color="danger")],
                                    style={
                                        "padding": "0",
                                        "margin": "0",
                                        "margin-left": "15px"
                                    },
                                )
                            ]),
                    dbc.Col(style={"textAlign": "center",
                                   "margin": "0",
                                   "padding": "0"
                                   },
                            width=4,
                            children=dbc.Row(style={"width": "100%",
                                                    "margin": "0",
                                                    "padding": "0"},
                                             children=[
                                                 dbc.Col(style={"textAlign": "center",
                                                                "margin": "0",
                                                                "padding": "0"
                                                                },
                                                         width=2,
                                                         children=[html.Img(style={"padding": "0",
                                                                                   "margin": "0",
                                                                                   "max_height": "40px",
                                                                                   "max-width": "40px"
                                                                                   },
                                                                            src='data:image/png;base64,{}'.format(
                                                                                encoded_image))]),
                                                 dbc.Col(style={"textAlign": "center",
                                                                "margin": "0",
                                                                "padding": "0"
                                                                },
                                                         width=5,
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

        dbc.Row(style={"width": "100%", "margin": "0", "padding": "0"},
                children=[
                    dbc.Col(style={"textAlign": "center",
                                   "height": "89vh",
                                   "minHeight": "89vh",
                                   "maxHeight": "89vh",
                                   "overflowY": "scroll",
                                   "margin": "0",
                                   "padding": "0"
                                   },
                            width=8,
                            className="no-scrollbars",
                            children=column_left()),
                    dbc.Col(style={"textAlign": "center",
                                   "height": "89vh",
                                   "minHeight": "89vh",
                                   "maxHeight": "89vh",
                                   "overflowY": "scroll",
                                   "margin": "0",
                                   "padding": "0"},
                            className="no-scrollbars",
                            width=4,
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
                    dbc.Input(type="text", id="example-api-key", placeholder="Enter API-key"),
                ],
                className="mr-3",
            ),
            dbc.FormGroup(
                [
                    dbc.Label("API_secret", className="mr-2"),
                    dbc.Input(type="text", id="example-api-secret", placeholder="Enter API-secret"),
                ],
                className="mr-3",
            ),
            dbc.Button("Сохранить", id="save_api", color="primary"),
        ],
        inline=True,
    )

    cont = [dbc.Row(style={"width": "100%",
                           "margin": "0",
                           "margin-bottom": "50px",
                           "padding": "0"},
                    no_gutters=False,
                    children=form),

            dbc.Row(style={"width": "100%",
                           "margin": "0",
                           "padding": "0"},
                    justify="center",
                    align="center",
                    no_gutters=False,
                    children=sub_column_left()),
            ]

    return cont


def sub_column_left():
    data = dbrools.get_active_data()

    cards = []
    print(data, "\n\n")
    for k, v in enumerate(data):
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

        row = dbc.Row(style={"width": "60%",
                             "margin": "0",
                             "padding": "0"},
                      no_gutters=False,
                      children=[
                          dbc.Col(width=1, children=[
                              my_img
                          ]),

                          dbc.Col(width=1, children=[
                              html.H5(v["symbol"],
                                      # id={"type": "symbol_name", "index": k}
                                      )
                          ]),

                          dbc.Col(width=3, children=[
                              dbc.Badge(v["side"],
                                        # id={"type": "symbol_side", "index": k},
                                        color="success" if v["side"] == "buy" else "danger", className="mr-1"),
                          ]),

                          dbc.Col(width=3, children=[
                              dbc.Input(type="number",
                                        id={"type": "symbol_amount", "index": k},
                                        # value=str(v["amount"])
                                        ),
                          ]),

                          dbc.Col(width=4, children=[
                              dbc.Button(my_button,
                                         # id={"type": "symbol_button", "index": k},
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
                       "height": "40vh",
                       "minHeight": "40vh",
                       "maxHeight": "40vh",
                       "overflowY": "scroll",
                       "margin": "0",
                       "padding": "0"},
                className="no-scrollbars",
                children=trade_history()),
    ]

    return cont


def my_wallet():
    pic_cards = []
    balances = dbrools.get_my_balances()

    if balances:
        # print(balances, "\n\n")
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
        child = html.Tr([
            html.Th([html.H5(v["symbol"], style={"min-width": "70px"})], style={"padding": "0", "margin": "0"}),
            html.Th([html.P("{0:.3f}".format(float(v["amount"])), style={"min-width": "70px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([html.P("{0:.3f}".format(float(v["price"])), style={"min-width": "70px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([dbc.Badge(v["direct"], style={"min-width": "70px"},
                               color="success" if v["direct"] == "BUY" else "danger")],
                    style={"padding": "0", "margin": "0"}),
            html.Th([html.P(v["date"], style={"min-width": "70px"})], style={"padding": "0", "margin": "0"}),
        ])

        my_list.append(child)

    return my_list
