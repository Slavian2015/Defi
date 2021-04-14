# -*- coding: utf-8 -*-
import json
import time

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import sys, base64, os
import plotly.express as px
import dbrools

sys.path.insert(0, r'/usr/local/WB')
main_path_data = os.path.expanduser('/usr/local/WB/dashboard/assets/')
main_path_data2 = os.path.expanduser('/usr/local/WB/data/')
symbols = ["ETHUPUSDT", "BTC", "ETH",
           "ETHDOWNUSDT", "EOS", "BNB",
           "LINK", "FIL", "YFI",
           "DOT", "SXP", "UNI",
           "LTC", "ADA", "AAVE"]


def my_view():
    # interval = dcc.Interval(id='interval', interval=10000, n_intervals=0)
    layout = [
        # interval,
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
    cont = dbc.Row(style={"width": "100%", "margin": "0", "padding": "0"},
                   children=[
                       dbc.Col(style={"textAlign": "center",
                                      "height": "100vh",
                                      "minHeight": "100vh",
                                      "maxHeight": "100vh",
                                      "overflowY": "scroll",
                                      "margin": "0",
                                      "padding": "0"
                                      },
                               width=6,
                               className="no-scrollbars",
                               children=column_left()),
                       dbc.Col(style={"textAlign": "center",
                                      "height": "100vh",
                                      "minHeight": "100vh",
                                      "maxHeight": "100vh",
                                      "overflowY": "hidden",
                                      "margin": "0",
                                      "padding": "0"},
                               width=6,
                               children=column_right()),
                   ],
                   no_gutters=True)

    return cont


def column_left():
    interval = dcc.Interval(id='interval_graf', interval=10000, n_intervals=0)
    cont = [
        interval,
        html.Div(style={'display': 'none'}, children=html.P("", id='symbol1')),
        html.Div(style={'display': 'none'}, children=html.P("", id='symbol2')),
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       "padding": "0"},
                id="full_list",
                no_gutters=False,
                children=full_list()),
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       "padding": "0"},
                no_gutters=False,
                id="sub_column_left",
                children=sub_column_left()),
    ]

    return cont


def full_list():
    my_balance = dbrools.get_my_balances()

    balance = float(my_balance['USDT'])
    trade = float(my_balance['ETHUP'])
    trade2 = float(my_balance['ETH'])
    time.sleep(0.5)
    a_file1 = open(main_path_data2 + "bal.json", "r")
    rools = json.load(a_file1)
    a_file1.close()

    if rools["bin"] == 5000:
        bin = "OFF"
    else:
        bin = "ON"

    card = dbc.Card(color="secondary",
                    style={"width": "100%",
                           "padding": "0",
                           "margin": "10px",
                           "margin-bottom": "0px"
                           },
                    inverse=True,
                    children=[
                        dbc.CardHeader(
                            style={"width": "100%",
                                   "padding": "0",
                                   "margin": "0",
                                   "color": "secondary",
                                   },
                            children=dbc.Row([dbc.Col(html.H4("USDT  : {0:.2f}".format(balance),
                                                              style={"color": "#fff",
                                                                     "text-align": "center",
                                                                     "padding": "0",
                                                                     "margin": "0", }),
                                                      style={"text-align": "center",
                                                             "margin": "0",
                                                             "padding": "0"},
                                                      width=3),
                                              dbc.Col(html.H4("ETHUP  : {0:.2f}".format(trade),
                                                              style={"color": "#fc1800",
                                                                     "text-align": "center",
                                                                     "padding": "0",
                                                                     "margin": "0", }),
                                                      style={"text-align": "center",
                                                             "margin": "0",
                                                             "padding": "0",
                                                             },
                                                      width=3),
                                              dbc.Col(html.H4("ETH  : {0:.2f}".format(trade2),
                                                              style={"color": "#fff",
                                                                     "text-align": "center",
                                                                     "padding": "0",
                                                                     "margin": "0", }),
                                                      style={"text-align": "center",
                                                             "margin": "0",
                                                             "padding": "0"},
                                                      width=3),
                                              dbc.Col(html.H4("{}".format(bin), style={"color": "#09ff3b",
                                                                                              "text-align": "center",
                                                                                              "padding": "0",
                                                                                              "margin": "0", }),
                                                      style={"text-align": "center",
                                                             "padding-left": "25px",
                                                             "margin": "0",
                                                             "padding": "0"},
                                                      width=3),
                                              ],
                                             no_gutters=False,
                                             style={"width": "100%",
                                                    "margin": "0",
                                                    "padding": "0"},
                                             )
                        ),
                    ])

    return card


def sub_column_left():
    df = pd.read_csv(os.path.expanduser('/usr/local/WB/data/prices_bd.csv'))
    trend = new_trend(df, 1)
    trend_up = new_trend(df, 2)

    cont = [
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       "padding": "0"},
                no_gutters=False,
                children=trend),
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       "padding": "0"},
                no_gutters=False,
                children=trend_up),
    ]

    return cont


def column_right():
    card = dbc.Card(account_list_tabs(),
                    color="primary",
                    style={"width": "100%",
                           "min-height": "100%",
                           },
                    inverse=True)

    cont = [
        dbc.Row(style={"width": "100%",
                       "height": "55vh",
                       "minHeight": "55vh",
                       "maxHeight": "55vh",
                       "overflowY": "hidden",
                       "padding": "0"},
                children=card),
        dbc.Row(style={"width": "100%",
                       "height": "10vh",
                       "minHeight": "10vh",
                       "maxHeight": "10vh",
                       "overflowY": "hidden",
                       # "margin": "0",
                       "padding": "0"},
                id="main_buttons",
                children=start_buttons_card()),
        dbc.Row(style={"width": "100%",
                       "height": "5vh",
                       "minHeight": "5vh",
                       "maxHeight": "5vh",
                       "overflowY": "hidden",
                       # "margin": "0",
                       "padding": "0"},
                children=[]),
        dbc.Row(style={"width": "100%",
                       "height": "30vh",
                       "minHeight": "30vh",
                       "maxHeight": "30vh",
                       "overflowY": "hidden",
                       "padding": "0",
                       "margin": "0"},
                justify="center",
                id="order_cards",
                children=order_card())]

    return cont


def start_buttons_card(b1=False, b2=False, b3=False, b4=False):
    card = dbc.Card(children=[
        dbc.CardBody(dbc.Row(children=[
            dbc.Col(dbc.Button("OFF",
                               # href="/admin",
                               id="parser_on",
                               style={
                                   "width": "100%",
                                   "minWidth": "100%",
                                   "maxWidth": "100%"},
                               color="success",
                               disabled=False)),
            # dbc.Col(dbc.Button("PARSER",
            #                    id="parser_off",
            #                    style={
            #                        "width": "100%",
            #                        "minWidth": "100%",
            #                        "maxWidth": "100%"},
            #                    color="danger",
            #                    disabled=b2)),
            dbc.Col(dbc.Button("BALANCE",
                               id="balance_btn",
                               style={
                                   "width": "100%",
                                   "minWidth": "100%",
                                   "maxWidth": "100%"},
                               color="warning",
                               disabled=False)),
            dbc.Col(dbc.Button("REGIM",
                               id="regim_on",
                               style={
                                   "width": "100%",
                                   "minWidth": "100%",
                                   "maxWidth": "100%"},
                               color="success",
                               disabled=b3)),
            dbc.Col(dbc.Button("REGIM",
                               id="regim_off",
                               style={
                                   "width": "100%",
                                   "minWidth": "100%",
                                   "maxWidth": "100%"},
                               color="danger",
                               disabled=b4)),

        ],
            style={"padding": "0",
                   "margin": "0"},
        ))],
        color="primary",
        style={"width": "100%",
               "min-height": "100%"},
        inverse=True)

    return card


def order_card(symbol1="ETHUPUSDT", symbol2="ETHDOWNUSDT"):

    card = [dbc.Col(dbc.Card(order_card_body(symbol=symbol1,
                                             price=None,
                                             amount=None),
                             color="primary",
                             style={"width": "100%",
                                    "min-height": "100%"},
                             inverse=True), width=6),
            dbc.Col(dbc.Card(order_card_body(symbol=symbol2,
                                             price=None,
                                             amount=None),
                             color="primary",
                             style={"width": "100%",
                                    "min-height": "100%"},
                             inverse=True), width=6)]
    return card


def order_card_body(symbol=None, price=None, amount=None):
    tre = html.Datalist(
        id=f'list-suggested-inputs-{symbol}',
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


def account_list_tabs():
    tabs_all = [
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label="HISTORY", tab_id="1", tab_style={"margin-left": "auto", "margin-top": "-10px",
                                                                    "margin-right": "auto"}),
                    dbc.Tab(label="OPEN", tab_id="2", tab_style={"margin-left": "auto", "margin-top": "-10px",
                                                                 "margin-right": "auto"})
                ],
                id="account-tabs",
                card=True,
                active_tab="1",
                style={"max-height": "fit-content"}
            )
        ),
        dbc.CardBody(card_body_acc(),
                     id='acc_tabs_list',
                     className="no-scrollbars",
                     style={"max-height": "100%",
                            "height": "200px",
                            "padding": "0",
                            "overflow-y": "scroll"})
    ]
    return tabs_all


def card_body_acc(card='1'):
    if card == "1":
        items = my_history()
    else:
        items = my_open()

    result = dbc.ListGroup(children=[
        dbc.ListGroupItem(children=i,
                          n_clicks=0,
                          action=True) for i in items])

    return result


def my_history():
    my_list = []

    items = dbrools.get_history_data()

    if not items:
        items = [{
            "date": "2021-01-20",
            "direct": 0,
            "kurs": 0,
            "balance": 0
        }
        ]

    for v in items:

        child = [dbc.Row([
            dbc.Col(html.P(v['date'],
                           style={"padding": "0",
                                  "margin": "0"}),
                    style={"padding": "0", "margin": "0"},
                    width={"size": 5}),
            dbc.Col(html.P("{}".format(v['direct']),
                           style={"padding": "0", "font-size": "12px", "margin": "0"}),
                    style={"padding": "0", "margin": "0"},
                    width={"size": 2}),
            dbc.Col(html.P("{:.2f}".format(v['kurs']),
                           style={"padding": "0", "font-size": "12px", "margin": "0"}),
                    style={"padding": "0", "margin": "0"},
                    width={"size": 2}),
            dbc.Col(html.P("{:.2f}".format(v['balance']),
                           style={"padding": "0", "color": "green", "margin": "0"}),
                    style={"padding": "0", "margin": "0"},
                    width={"size": 3}),
        ])]

        my_list.append(child)

    return my_list


def my_open():
    my_list = []

    items = []

    if not items:
        items = [
            {
                "Time": 0,
                "Start": 0
            }
        ]

    for v in items:
        child = [dbc.Row([
            dbc.Col(html.P(v['Time'], style={"padding": "0", "margin": "0"}),
                    style={"padding": "0", "margin": "0"},
                    width={"size": 6}),
            dbc.Col(html.P(v['Start'], style={"padding": "0", "margin": "0"}),
                    style={"padding": "0", "margin": "0"},
                    width={"size": 6}),
        ])]

        my_list.append(child)

    return my_list


def new_trend(df, n):
    if n == 1:
        graf = my_trend_graf(df)
    else:
        graf = my_trend_spread(df)

    card = dbc.Card(graf,
                    color="primary",
                    style={"width": "100%",
                           "padding": "0",
                           "margin": "10px",
                           "margin-bottom": "0px"
                           },
                    inverse=True)

    return [card]


def my_trend_graf(df):
    def my_graph_trend():
        annotations = []

        annotations.append(dict(xref='paper', x=1.0, y=df['roll_x60'].iloc[-1],
                                xanchor='left', yanchor='middle',
                                text='{:.2f}'.format(df['roll_x60'].iloc[-1]),
                                font=dict(family='Balto',
                                          size=16,
                                          color='rgb(66,135,245)'),
                                showarrow=False))
        annotations.append(dict(xref='paper', x=1.0, y=df['roll_x300'].iloc[-1],
                                xanchor='left', yanchor='middle',
                                text='{:.2f}'.format(df['roll_x300'].iloc[-1]),
                                font=dict(family='Balto',
                                          size=16,
                                          color='rgb(255,81,0)'),
                                showarrow=False))

        annotations.append(dict(xref='paper', x=1.0, y=df['roll_x500'].iloc[-1],
                                xanchor='left', yanchor='middle',
                                text='{:.2f}'.format(df['roll_x500'].iloc[-1]),
                                font=dict(family='Balto',
                                          size=16,
                                          color='rgb(255,81,0)'),
                                showarrow=False))
        fig = px.line(df,
                      x='timestamp',
                      y=['roll_x60', 'roll_x300', 'roll_x500'],
                      line_shape="linear",
                      color_discrete_map={
                          "track": "black"},
                      template='plotly_dark').update_layout(
            {
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                "height": 300,
                "yaxis_range": [1000, 1600],
                "margin": dict(l=0, r=60, t=0, b=0, pad=10),
                "showlegend": False,
                "xaxis": dict(
                    title_text="",
                    showgrid=False,
                    ticks='outside',
                    showticklabels=False,
                    visible=False,
                    fixedrange=True,
                    scaleanchor="x",
                    scaleratio=1,
                ),
                "yaxis": dict(
                    side="right",
                    title_text="",
                    ticks='outside',
                    showticklabels=False,
                    showline=False,
                ),
                "title": {
                    "xref": "paper",
                    "x": 0.1,
                    "xanchor": "center",
                    "yref": "paper",
                    "y": 0.1,
                    "yanchor": "bottom"
                },
            }).update()
        fig.update_yaxes(nticks=5)

        fig.update_layout(hovermode="x", annotations=annotations)

        fig.add_scatter(x=df['timestamp'],
                        y=df['roll_x60'],
                        hoverinfo="skip",
                        # fill='tonexty',
                        mode='lines')
        fig.add_scatter(x=df['timestamp'],
                        y=df['roll_x300'],
                        hoverinfo="skip",
                        fill='tonexty',
                        mode='lines'),

        fig.add_scatter(x=df['timestamp'],
                        y=df['roll_x500'],
                        hoverinfo="skip",
                        # fill='tonexty',
                        mode='lines'),
        return fig

    tabs_all = [
        dbc.CardBody(
            dcc.Graph(config={'displayModeBar': False},
                      style={"height": "40vh", "margin": "0"},
                      figure=my_graph_trend()))]
    return tabs_all


def my_trend_spread(df):

    # print("\n\n\n", df.head(5))
    def my_graph_trend():
        annotations = []

        # annotations.append(dict(xref='paper', x=1.0, y=df['x1'].iloc[-1],
        #                         xanchor='left', yanchor='middle',
        #                         text='{:.2f}'.format(df['x1'].iloc[-1]),
        #                         font=dict(family='Balto',
        #                                   size=16,
        #                                   color='rgb(66,135,245)'),
        #                         showarrow=False))
        annotations.append(dict(xref='paper', x=1.0, y=df['x21'].iloc[-1],
                                xanchor='left', yanchor='middle',
                                text='{:.2f}'.format(df['x21'].iloc[-1]),
                                font=dict(family='Balto',
                                          size=16,
                                          color='rgb(255,81,0)'),
                                showarrow=False))

        annotations.append(dict(xref='paper', x=1.0, y=df['x31'].iloc[-1],
                                xanchor='left', yanchor='middle',
                                text='{:.2f}'.format(df['x31'].iloc[-1]),
                                font=dict(family='Balto',
                                          size=16,
                                          color='rgb(255,81,0)'),
                                showarrow=False))

        fig = px.line(df,
                      x='timestamp',
                      y=['x21', "x31"],
                      line_shape="linear",
                      # hover_data={"1 HOUR :": (':.3f', df["x1"]),
                      #             'variable': False,
                      #             'timestamp': False,
                      #             'value': False,
                      #             "2 days :": (':.3f', df["x21"]),
                      #             "4 days": (':.3f', df["x31"])},
                      template='plotly_dark').update_layout(
            {
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                "height": 300,
                "margin": dict(l=0, r=60, t=0, b=0, pad=10),
                "showlegend": False,
                "xaxis": dict(
                    title_text="",
                    showgrid=False,
                    ticks='outside',
                    showticklabels=False,
                    visible=False,
                    fixedrange=True
                ),
                "yaxis": dict(
                    side="right",
                    title_text="",
                    ticks='outside',
                    showticklabels=False,
                    fixedrange=True,
                    showline=False,
                ),
                "title": {
                    "xref": "paper",
                    "x": 0.5,
                    "xanchor": "center",
                    "yref": "paper",
                    "y": 0.5,
                    "yanchor": "bottom"
                },
            }).update(layout_autosize=True)
        fig.update_yaxes(nticks=20)
        fig.update_layout(hovermode="x", annotations=annotations)

        fig.add_scatter(x=df['timestamp'],
                        y=df['x21'],
                        hoverinfo="skip",
                        # fill='tonexty',
                        mode='lines')
        fig.add_scatter(x=df['timestamp'],
                        y=df['x31'],
                        hoverinfo="skip",
                        fill='tonexty',
                        mode='lines')


        return fig

    tabs_all = [
        dbc.CardBody(
            dcc.Graph(config={'displayModeBar': False},
                      style={"height": "40vh", "margin": "0"},
                      figure=my_graph_trend()))]
    return tabs_all

