# -*- coding: utf-8 -*-
import json
import time

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import sys, base64, os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

sys.path.insert(0, r'/usr/local/WB')
main_path_data = os.path.expanduser('/usr/local/WB/dashboard/assets/')
main_path_data2 = os.path.expanduser('/usr/local/WB/data/')
symbols = ["ETHUPUSDT", "BTC", "ETH",
           "ETHDOWNUSDT", "EOS", "BNB",
           "LINK", "FIL", "YFI",
           "DOT", "SXP", "UNI",
           "LTC", "ADA", "AAVE"]


# df = px.data.gapminder()
#
# print(df.head(50))


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
                   children=column(),
                   no_gutters=True)

    return cont


def column():
    df = pd.read_csv(os.path.expanduser('/usr/local/WB/data/prices_bd.csv'))
    trend, graf = new_trend(df)

    cont = [
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       "padding": "0"},
                no_gutters=False,
                children=[
                       dbc.Col(style={"textAlign": "center",
                                      # "height": "100vh",
                                      # "minHeight": "100vh",
                                      # "maxHeight": "100vh",
                                      # "overflowY": "scroll",
                                      "margin": "0",
                                      "padding": "0"
                                      },
                               width=3,
                               className="no-scrollbars",
                               children=trend),
                       dbc.Col(style={"textAlign": "center",
                                      # "height": "100vh",
                                      # "minHeight": "100vh",
                                      # "maxHeight": "100vh",
                                      # "overflowY": "hidden",
                                      "margin": "0",
                                      "padding": "0"},
                               width=3,
                               children=trend),
                       dbc.Col(style={"textAlign": "center",
                                      # "height": "100vh",
                                      # "minHeight": "100vh",
                                      # "maxHeight": "100vh",
                                      # "overflowY": "scroll",
                                      "margin": "0",
                                      "padding": "0"
                                      },
                               width=3,
                               className="no-scrollbars",
                               children=trend),
                       dbc.Col(style={"textAlign": "center",
                                      # "height": "100vh",
                                      # "minHeight": "100vh",
                                      # "maxHeight": "100vh",
                                      # "overflowY": "hidden",
                                      "margin": "0",
                                      "padding": "0"},
                               width=3,
                               children=trend),
                   ],
                ),
        dbc.Row(style={"width": "100%",
                       "margin": "0",
                       "padding": "0"},
                no_gutters=False,
                children=[
                       dbc.Col(style={"textAlign": "center",
                                      # "height": "100vh",
                                      # "minHeight": "100vh",
                                      # "maxHeight": "100vh",
                                      # "overflowY": "scroll",
                                      "margin": "0",
                                      "padding": "0"
                                      },
                               width=3,
                               className="no-scrollbars",
                               children=graf),
                       dbc.Col(style={"textAlign": "center",
                                      # "height": "100vh",
                                      # "minHeight": "100vh",
                                      # "maxHeight": "100vh",
                                      # "overflowY": "hidden",
                                      "margin": "0",
                                      "padding": "0"},
                               width=3,
                               children=graf),
                       dbc.Col(style={"textAlign": "center",
                                      # "height": "100vh",
                                      # "minHeight": "100vh",
                                      # "maxHeight": "100vh",
                                      # "overflowY": "scroll",
                                      "margin": "0",
                                      "padding": "0"
                                      },
                               width=3,
                               className="no-scrollbars",
                               children=graf),
                       dbc.Col(style={"textAlign": "center",
                                      # "height": "100vh",
                                      # "minHeight": "100vh",
                                      # "maxHeight": "100vh",
                                      # "overflowY": "hidden",
                                      "margin": "0",
                                      "padding": "0"},
                               width=3,
                               children=graf),
                   ],
                ),
    ]

    return cont


def new_trend(df):
    graf, graf2 = my_trend_spread(df)

    card = dbc.Card(
        graf,
        color="primary",
        style={"width": "100%",
               "padding": "0",
               "margin": "0",
               "margin-bottom": "0px"
               },
        inverse=True)

    card2 = html.Div(
        graf2,
        style={"width": "100%",
               "padding": "0",
               "margin": "0",
               "margin-bottom": "0px"
               },
    )

    return card, card2


def my_trend_spread(df):

    df["sell"] = np.nan
    df["sell"].iloc[-1] = df["x31"].iloc[-1] + 3
    df["buy"] = np.nan
    df["buy"].iloc[-1000] = df["x31"].iloc[-1000] - 3

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

        fig.add_trace(go.Scatter(x=df['timestamp'], y=df["sell"],
                                 mode='markers',
                                 marker_line_color="midnightblue",
                                 marker_line_width=2,
                                 marker_symbol=6,
                                 marker_color="red",
                                 marker_size=20,
                                 name='markers'))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df["buy"],
                                 mode='markers',
                                 marker_line_color="midnightblue",
                                 marker_line_width=2,
                                 marker_symbol=5,
                                 marker_color="limegreen",
                                 marker_size=20,
                                 name='markers'))

        fig.update_layout(
            {
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                "height": 200,
                "margin": dict(l=0, r=20, t=0, b=0, pad=0),
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
                    'text': "<b>ETH</b>",
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
                          title_font_size=26,
                          )

        return fig

    new_fig = new()

    tabs_all = [
        dbc.CardBody(
            dcc.Graph(
                # style={"height": "90vh", "margin": "0"},
                figure=new_fig))]

    tabs_fig = dcc.Graph(figure=new_fig)

    return tabs_all, tabs_fig
