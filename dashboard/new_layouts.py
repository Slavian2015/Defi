# -*- coding: utf-8 -*-
import base64
import os
import sys

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import json
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
                                                    width=6,
                                                    children=[
                                                        dbc.Button("BALANCE", id="balance_btn", color="warning")]),
                                            dbc.Col(style={"textAlign": "center",
                                                           "margin": "0",
                                                           "padding": "0"
                                                           },
                                                    width=6,
                                                    children=[
                                                        dbc.Button("START", id="start_btn", color="success")])
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
                                   "maxHeight": "89vh",
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
                                                    "padding": "0",
                                                    "display": "block"},
                                             id="new_trade_history",
                                             className="no-scrollbars",
                                             children=new_trade_history())),
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
                       "margin": "10px",
                       "padding": "0"},
                justify="center",
                align="center",
                # id="new_left_side",
                # no_gutters=False,
                children=sub_column_left()),
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
    ]

    return cont


def sub_column_left():
    main_path = f'/usr/local/WB/dashboard/data/settings.json'

    with open(main_path, 'r', encoding='utf-8') as outfile:
        data = json.load(outfile)

    cards = []
    for k, v in data.items():
        my_img = html.Img(style={"padding": "0",
                                 "margin": "0",
                                 "max_height": "25px",
                                 "max-width": "25px"
                                 },
                          src='data:image/png;base64,{}'.format(
                              base64.b64encode(open(main_path_data + f'{k.split("USDT")[0]}.png', 'rb').read()).decode(
                                  'ascii')))

        if v:
            my_button_color = "danger"
        else:
            my_button_color = "success"

        my_button = dbc.Row(style={
            "width": "100%",
            "margin": "10px",
            "padding": "0"},
            children=[dbc.Col(width=4,
                              style={
                                  "margin": "0",
                                  "padding": "0"},
                              children=[my_img]),
                      dbc.Col(width=8,
                              style={
                                  "margin": "0",
                                  "padding": "0"},
                              children=[
                                  html.H5(k.split("USDT")[0],
                                          id={"type": "symbol_name", "index": k})])])

        row = html.Div(dbc.Col(width=6,
                               children=dbc.Button(my_button,
                                                   style={
                                                       "min-width": "120px",
                                                       "margin": "0",
                                                       "padding": "0"},
                                                   id={"type": "symbol_button", "index": k},
                                                   color=my_button_color)))

        cards.append(row)

    return cards


def column_right():
    interval = dcc.Interval(id='interval_price', interval=5000, n_intervals=0)
    cont = [
        interval,
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


def new_trade_history():
    card = html.Div(

        dbc.Row(
        [
            dbc.Col(dbc.Card(history_main_card(), color="dark", style={"margin": "0",
                   "padding": "0"}, inverse=True)),
        ],
            style={"margin": "0",
                   "padding": "0"},
        ),
            style={"margin": "0",
                   "padding": "0"}


        # dbc.Row(
        #     [
        #         dbc.Col(dbc.Card(card_content, color="light")),
        #         dbc.Col(dbc.Card(card_content, color="dark", inverse=True)),
        #     ]
        # )
    )
    return card


def history_main_card():

    table_header = [
        html.Thead(html.Tr(
            [
                html.Th("COINS"),
                html.Th("Profit Deals"),
                html.Th("All Deals"),
                html.Th("Ratio"),
                html.Th("Commissions"),
                html.Th("Netto USD"),
                html.Th("PNL"),
            ],
            style={"font-size": "10px", "textAlign": "center",
                                   "margin": "0",
                                   "padding": "0"}),
            style={"margin": "0",
                   "padding": "0"}
        )

    ]

    table_body = [html.Tbody(my_new_trade_history(),
                            style={"margin": "0",
                                    "padding": "0"},
                             id="main_trade_table")]

    table = dbc.Table(table_header + table_body,
                      style={"width": "100%", 'border-collapse': 'collapse',"margin": "0",
                                    "padding": "0"},
                      className="no-scrollbars",
                      bordered=True,
                      # dark=True,
                      responsive=True)

    card_content = [
        dbc.CardBody(
            [table],
                            style={"margin": "0",
                                    "padding": "0",
                                   "min-width": "100%",}
        ),
    ]

    return card_content


def item_card_history():
    return


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
            html.Th([html.P("{0:.6f}".format(float(v["amount"])), style={"min-width": "50px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([html.P("{0:.6f}".format(float(v["price"])), style={"min-width": "50px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([dbc.Badge(v["direct"], style={"min-width": "50px"},
                               color="success" if v["direct"] == "BUY" else "danger")],
                    style={"padding": "0", "margin": "0"}),
            html.Th([html.P(v["date"], style={"min-width": "70px"})], style={"padding": "0", "margin": "0"}),
        ], style={"background-color": new_color})

        my_list.append(child)

    return my_list


def my_new_trade_history():
    my_list = []

    # items = dbrools.get_history_data()

    items = []
    if not items:
        items = [
            {
                       "symbol": "BTC",
                       "side": "LONG",
                       "priceIn": 100,
                       "priceOut": 102,
                       "result": 2,
                       "profit": 2,
                       "date": f"1625047065159"
                   },
            {
                       "symbol": "BTC",
                       "side": "LONG",
                       "priceIn": 102,
                       "priceOut": 103,
                       "result": 2,
                       "profit": 1,
                       "date": f"1625047065159"
                   },
            {
                       "symbol": "BTC",
                       "side": "LONG",
                       "priceIn": 105,
                       "priceOut": 104,
                       "result": 1,
                       "profit": -1,
                       "date": f"1625047065159"
                   },
            {
                       "symbol": "TRX",
                       "side": "LONG",
                       "priceIn": 100,
                       "priceOut": 100,
                       "result": 2,
                       "profit": 0,
                       "date": f"1625047065159"
                   },
        ]

    coins = []
    p_deals = []
    brutto = []

    for i in items:
        coins.append(i['symbol'])
        if i['result'] == 2:
            p_deals.append(i['profit'])
        brutto.append(i['profit'])

    ratio = round(len(p_deals) / len(brutto) * 100, 2)
    commissions = round(len(brutto) * 2 * 0.33, 2)
    netto = round(sum(brutto) - commissions, 2)
    pnl = round(netto / (60*len(set(coins))) * 100, 2)

    child = html.Tr([
            html.Th([html.P(len(set(coins)), style={"min-width": "30px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([html.P(len(p_deals), style={"min-width": "40px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([html.P(len(brutto), style={"min-width": "40px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([html.P(ratio, style={"min-width": "50px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([html.P(commissions, style={"min-width": "40px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([html.P(netto, style={"min-width": "40px"})],
                    style={"padding": "0", "margin": "0"}),
            html.Th([dbc.Badge(pnl, style={"min-width": "50px"}, color="success")],
                    style={"padding": "0", "margin": "0"})
    ])

    return child