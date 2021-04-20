# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import sys, base64, os
import plotly.graph_objects as go

sys.path.insert(0, r'/usr/local/WB')
main_path_data = os.path.expanduser('/usr/local/WB/dashboard/assets/')
main_path_data2 = os.path.expanduser('/usr/local/WB/data/')

symbols = ["LTCUSDT", "ETHUSDT", "BTCUSDT", "BNBUSDT"]
symbols2 = ["LTC", "ETH", "BTC", "BNB"]


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
    interval = dcc.Interval(id='interval_graf_long_short', interval=70000, n_intervals=0)
    cont = [
        interval,
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       "padding": "0"},
                children=row1,
                id="graf_long",
                no_gutters=True),
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       "padding": "0"},
                children=row2,
                id="graf_short",
                no_gutters=True),
    ]
    return cont


def columns():
    cont_long = []
    cont_short = []
    for i in symbols2:

        df = pd.read_csv(os.path.expanduser(f'/usr/local/WB/data/{i}USDT.csv'))

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

    df = df.tail(int(1440*2))

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
                    showticklabels=True,
                    showgrid=False,
                    fixedrange=True,
                    showline=False,
                    color="#fff"
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

    df = df.tail(200)

    def new():
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df['timestamp'], y=df["ttt"],
                                 mode='lines',
                                 name='ttt',
                                 fill='tonexty',
                                 line_color='limegreen',
                                 ))

        fig.add_trace(go.Scatter(x=df['timestamp'], y=df["x5"],
                                 mode='lines',
                                 name='x5',
                                 line_color='red'
                                 ))

        fig.update_layout(
            {
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                "height": 300,
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
                    showticklabels=True,
                    showgrid=True,
                    fixedrange=True,
                    showline=False,
                    color="#fff"
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
    cont_long = []
    cont_short = []
    for i in symbols2:

        df = pd.read_csv(os.path.expanduser(f'/usr/local/WB/data/{i}USDT.csv'))

        cont_long.append(graf_long(i, df))
        cont_short.append(graf_short(i, df))

    result = cont_long + cont_short

    return result

