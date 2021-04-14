# -*- coding: utf-8 -*-
import json
import time
import dbrools
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import sys, base64, os
import plotly.graph_objects as go
import numpy as np

sys.path.insert(0, r'/usr/local/WB')
main_path_data = os.path.expanduser('/usr/local/WB/dashboard/assets/')
main_path_data2 = os.path.expanduser('/usr/local/WB/data/')

symbols = ["ETHUSDT", "EOSUSDT", "BNBUSDT", "LTCUSDT"]
symbols2 = ["ETH", "EOS", "BNB", "LTC"]


def my_view():
    interval = dcc.Interval(id='interval_graf_full', interval=10000, n_intervals=0)
    layout = [
        interval,
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
    row1, row2 = columns()
    row3 = order_card()
    cont = [dbc.Row(style={"width": "100%",
                           "margin": "0",
                           "padding": "0"},
                    children=row1,
                    no_gutters=True),
            dbc.Row(style={"width": "100%",
                           "margin": "0",
                           "padding": "0"},
                    children=row2,
                    no_gutters=True),
            dbc.Row(style={"width": "100%",
                           "margin": "0",
                           "padding": "0"},
                    children=row3,
                    no_gutters=True),
            ]
    return cont


def columns():
    d = dbrools.get_full_data()

    cont_long = []
    cont_short = []
    for i in symbols2:
        df = pd.DataFrame({
            'timestamp': d["data"][f"{i}USDT"]['timestamp'],
            'close': d["data"][f"{i}USDT"]['close']
        })
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        tabs_all_long = [
            dbc.CardBody(
                dcc.Graph(
                    id=f'graph_long_{i}',
                    # animate=True,
                    figure=graf_long(i, df)),
                style={
                    "padding": "0",
                    "margin": "0"})]

        card_long = dbc.Col(style={"textAlign": "center",
                                   "margin": "0",
                                   "padding": "0"
                                   },
                            width=3,
                            className="no-scrollbars",
                            children=dbc.Card(
                                tabs_all_long,
                                color="primary",
                                style={"width": "100%",
                                       "padding": "0",
                                       "margin": "0",
                                       "margin-bottom": "0px"
                                       },
                                inverse=True))

        cont_long.append(card_long)

        tabs_fig = dcc.Graph(
            id=f'graph_short_{i}',
            # animate=True,
            figure=graf_short(i, df))

        card = dbc.Col(style={"textAlign": "center",
                              "margin": "0",
                              "padding": "0"
                              },
                       width=3,
                       className="no-scrollbars",
                       children=html.Div(
                           tabs_fig,
                           style={"width": "100%",
                                  "padding": "0",
                                  "margin": "0",
                                  "margin-bottom": "0px"
                                  },
                       ))
        cont_short.append(card)

    return cont_long, cont_short


def graf_long(symbol, df):
    df['roll_x60'] = df["close"].rolling(60).mean()
    df['roll_x60x'] = df["roll_x60"].rolling(60).mean()

    df['roll_x300'] = df["close"].rolling(int(1440 * 2)).mean()
    df['roll_x500'] = df["close"].rolling(int(1440 * 5)).mean()

    df = df.dropna()

    df["x1"] = df["roll_x60x"] - df["roll_x300"]
    df["x21"] = df["roll_x60x"] - df["roll_x500"]
    df["x31"] = df["roll_x300"] - df["roll_x500"]

    df = df.tail(10000)

    # df["sell"] = np.nan
    # df["buy"] = np.nan
    #
    # fil_sell = df[(df['x31'] > df['x21']) & (df['x21'] > df['x31'].shift(1))].index
    # fil_buy = df[(df['x31'] < df['x21']) & (df['x21'] < df['x31'].shift(1))].index
    #
    # df.loc[fil_sell, "sell"] = df.loc[fil_sell, "x31"]
    # df.loc[fil_buy, "buy"] = df.loc[fil_buy, "x31"]

    def new():
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df['timestamp'], y=df["x31"],
                                 mode='lines',
                                 name='x31',
                                 line_color='red'
                                 ))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df["x21"],
                                 mode='lines',
                                 name='x21',
                                 fill='tonexty',
                                 line_color='limegreen',
                                 ))

        # fig.add_trace(go.Scatter(x=df['timestamp'], y=df["sell"],
        #                          mode='markers',
        #                          marker_line_color="midnightblue",
        #                          marker_line_width=2,
        #                          marker_symbol=6,
        #                          marker_color="red",
        #                          marker_size=20,
        #                          name='markers'))
        # fig.add_trace(go.Scatter(x=df['timestamp'], y=df["buy"],
        #                          mode='markers',
        #                          marker_line_color="midnightblue",
        #                          marker_line_width=2,
        #                          marker_symbol=5,
        #                          marker_color="limegreen",
        #                          marker_size=20,
        #                          name='markers'))
        fig.update_layout(
            {
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                "height": 200,
                "margin": dict(l=0, r=5, t=0, b=0, pad=0),
                "showlegend": False,
                "xaxis": dict(
                    title_text="",
                    showgrid=False,
                    # ticks='outside',
                    showticklabels=False,
                    visible=True,
                    fixedrange=True
                ),
                "yaxis": dict(
                    side="right",
                    title_text="",
                    # ticks='outside',
                    showticklabels=False,
                    showgrid=False,
                    fixedrange=True,
                    showline=False,
                ),

                "title": {
                    'text': f"<b>{symbol}</b>",
                    "xref": "paper",
                    "x": 0.5,
                    "xanchor": "center",
                    "yref": "paper",
                    "y": 0.9,
                    "yanchor": "top"
                },
            }).update(layout_autosize=True)
        fig.update_layout(hovermode="x",
                          title_font_family="Arial",
                          title_font_color="white",
                          title_font_size=20,
                          )

        return fig

    new_fig = new()
    return new_fig


def graf_short(symbol, df):
    df['roll_x60'] = df["close"].rolling(60).mean()
    df['roll_x60x'] = df["roll_x60"].rolling(60).mean()
    df['roll_x5'] = df["close"].rolling(5).mean()
    df['roll_x15'] = df["close"].rolling(int(15)).mean()

    df = df.dropna()

    df["x5"] = df["roll_x5"] - df["roll_x60x"]
    df["x15"] = df["roll_x15"] - df["roll_x60x"]

    df["ttt"] = df['x5'] - df['x15']
    df["zero"] = 0

    df = df.tail(200)

    def new():
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df['timestamp'], y=df["ttt"],
                                 mode='lines',
                                 name='x21',
                                 fill='tonexty',
                                 line_color='limegreen',
                                 ))

        fig.update_layout(
            {
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                "height": 200,
                "margin": dict(l=0, r=5, t=0, b=0, pad=0),
                "showlegend": False,
                "xaxis": dict(
                    title_text="",
                    showgrid=False,
                    # ticks='outside',
                    showticklabels=False,
                    visible=True,
                    fixedrange=True
                ),
                "yaxis": dict(
                    side="right",
                    title_text="",
                    # ticks='outside',
                    showticklabels=False,
                    showgrid=False,
                    fixedrange=True,
                    showline=False,
                ),

                "title": {
                    'text': f"<b>{symbol}</b>",
                    "xref": "paper",
                    "x": 0.5,
                    "xanchor": "center",
                    "yref": "paper",
                    "y": 0.9,
                    "yanchor": "top"
                },
            }).update(layout_autosize=True)
        fig.update_layout(hovermode="x",
                          title_font_family="Arial",
                          title_font_color="white",
                          title_font_size=20,
                          )

        return fig

    new_fig = new()
    return new_fig


def refresh_grafs():
    d = dbrools.get_full_data()

    cont_long = []
    cont_short = []
    for i in symbols2:
        df = pd.DataFrame({
            'timestamp': d["data"][f"{i}USDT"]['timestamp'],
            'close': d["data"][f"{i}USDT"]['close']
        })
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        cont_long.append(graf_long(i, df))
        cont_short.append(graf_short(i, df))

    result = cont_long + cont_short

    return result


def order_card():
    card = []

    for i in symbols2:
        d = dbc.Col(dbc.Card(order_card_body(symbol=f"{i}UPUSDT",
                                             price=None,
                                             amount=None),
                             color="primary",
                             style={"width": "100%",
                                    "min-height": "100%"},
                             inverse=True), width=3)
        card.append(d)
    return card


# def order_card_body(symbol="ETHUSDT"):
#
#     data = {
#         symbol:
#             {"balance": 1800,
#              "status": "OFF"}
#     }
#
#     if data[symbol]['status'] == "OFF":
#         color = "danger"
#     else:
#         color = "success"
#
#     tabs_all = [
#         dbc.CardBody([
#             dbc.InputGroup([
#                 dbc.InputGroupAddon(html.P("balance",
#                                            style={"width": "100%"}),
#                                     style={"width": "80px"},
#                                     addon_type="prepend"),
#                 dbc.Input(value=data[symbol]['balance'],
#                           id={"type": "balance_mini_btn", "index": symbol},
#                           type="number")],
#                 style={"width": "100%"}),
#
#             dbc.InputGroup([
#                 dbc.InputGroupAddon(html.P("Status",
#                                            style={"width": "100%"}),
#                                     style={"width": "80px"},
#                                     addon_type="prepend"),
#                 dbc.Button(data[symbol]['status'],
#                            color=color,
#                            id={"type": "status_btn", "index": symbol},
#                 )],
#                 style={"width": "100%"})
#             ]),
#
#         dbc.CardFooter(
#             dbc.ButtonGroup(
#                 [dbc.Button("START",
#                             id={"type": "start_btn", "index": symbol},
#                             color="success"),
#                  dbc.Button("STOP",
#                             id={"type": "stop_btn", "index": symbol},
#                             color="danger")],
#                 style={"width": "100%",
#                        "padding": "0",
#                        "margin": "0"
#                        },
#             ),
#             style={"width": "100%",
#                    "padding": "0",
#                    "margin": "0"
#                    }),
#     ]
#     return tabs_all


def order_card_body(symbol=None, price=None, amount=None):
    tre = html.Datalist(
        id=f'list-suggested-inputs2-{symbol}',
        children=[html.Option(value=word) for word in symbols])

    tabs_all = [tre,
                dbc.CardBody([
                    dbc.InputGroup([
                        dbc.InputGroupAddon(html.P("Symbol",
                                                   style={"width": "100%"}),
                                            style={"width": "80px"},
                                            addon_type="prepend"),
                        dbc.Input(placeholder=symbol,
                                  value=symbol,
                                  id={"type": "order_sec_btn", "index": symbol},
                                  autoComplete='on',
                                  list=f'list-suggested-inputs-{symbol}',
                                  type="text"),
                    ]),
                    dbc.InputGroup([
                        dbc.InputGroupAddon(html.P("Цена", style={"width": "100%"}), style={"width": "80px"},
                                            addon_type="prepend"),
                        dbc.Input(placeholder=price,
                                  value=price,
                                  id={"type": "order_price_btn", "index": symbol},
                                  type="text")
                    ], style={"width": "100%"}),
                    dbc.InputGroup([
                        dbc.InputGroupAddon(html.P("К-во", style={"width": "100%"}), style={"width": "80px"},
                                            addon_type="prepend"),
                        dbc.Input(placeholder=amount,
                                  value=amount,
                                  id={"type": "order_qty_btn", "index": symbol},
                                  type="number"),
                    ]),
                    html.P("",
                           id={"type": "order_result", "index": symbol},
                           style={"width": "100%",
                                  "padding": "0",
                                  "margin": "0",
                                  "max-height": "20px",
                                  "overflow-y": "hidden"})

                ]),
                dbc.CardFooter(
                    dbc.ButtonGroup(
                        [dbc.Button("Купить",
                                    id={"type": "order_buy_btn", "index": symbol},
                                    color="success"),
                         dbc.Button("Продать",
                                    id={"type": "order_sell_btn", "index": symbol},
                                    color="danger")],
                        style={"width": "100%",
                               "padding": "0",
                               "margin": "0"
                               },
                    ),
                    style={"width": "100%",
                           "padding": "0",
                           "margin": "0"
                           }),
                ]
    return tabs_all
