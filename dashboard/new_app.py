import dash, json, sys, os, signal
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH, ALL
import flask
import new_layouts
import Orders
import subprocess
import threading
import warnings
import dbrools
from binance.client import Client

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
        return new_layouts.my_view()
    else:
        return "404"


# ###############################    REFRESH BALANCE    ##################################
@dash_app.callback([Output('usdt_balance', 'children')],
                   [Input('balance_btn', 'n_clicks')])
def trigger_balance(n1):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')
    if button_id[0] == 'balance_btn':
        new_keys = dbrools.my_keys.find_one()
        api_key = new_keys['bin']['key']
        api_secret = new_keys['bin']['secret']

        bclient = Client(api_key=api_key, api_secret=api_secret)

        Orders.my_balance(client=bclient)
        repons = dbrools.get_my_balances()
        return ["{0:.2f} $".format(float(repons['USDT']))]
    else:
        raise PreventUpdate


# ###############################    UPDATE KEYS    ##################################
@dash_app.callback([Output('save_api_telega_toast', 'is_open')],
                   [Input('save_api_telega', 'n_clicks')],
                   [State('example-api-key_telega', 'value'),
                    State('example-api-secret_telega', 'value')])
def trigger_balance(n1, api_key, api_secret):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')
    if button_id[0] == 'save_api_telega':
        if not api_key or not api_secret:
            dbrools.update_tel_keys(0, 0)
        else:
            dbrools.update_tel_keys(api_key, api_secret)
        return [True]
    else:
        raise PreventUpdate


@dash_app.callback([Output('save_api_bin_toast', 'is_open')],
                   [Input('save_api_bin', 'n_clicks')],
                   [State('example-api-key_bin', 'value'),
                    State('example-api-secret_bin', 'value')])
def trigger_balance2(n1, api_key, api_secret):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')
    if button_id[0] == 'save_api_bin':
        if not api_key or not api_secret:
            dbrools.update_bin_keys(0, 0)
        else:
            dbrools.update_bin_keys(api_key, api_secret)
        return [True]
    else:
        raise PreventUpdate


# ###############################    Refresh History   ##################################
@dash_app.callback(
    Output('new_trade_history', 'children'),
    [Input("interval_price", 'n_intervals')])
def trigger_by_modify(n1):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')

    if button_id[0] == 'interval_price':
        card = new_layouts.new_trade_history()
        return card
    else:
        raise PreventUpdate


# ##############################   Orders   ##################################
@dash_app.callback(
    [Output({'type': 'symbol_button', 'index': MATCH}, 'color')],
    [Input({'type': 'symbol_button', 'index': MATCH}, 'n_clicks')],
    [State({'type': 'symbol_name', 'index': MATCH}, 'children'),
     State({'type': 'symbol_button', 'index': MATCH}, 'color')]
)
def toggle_modal(n1, symbol, old_btn_color):
    trigger = dash.callback_context.triggered[0]
    button = trigger["prop_id"].split(".")[0]

    if not button:
        raise PreventUpdate
    else:
        if type(button) is str:
            button = json.loads(button.replace("'", "\""))
        if button["type"] == 'symbol_button':
            if old_btn_color == "success":

                main_path_settings = f'/usr/local/WB/dashboard/data/settings.json'

                a_file1 = open(main_path_settings, "r")
                rools = json.load(a_file1)
                a_file1.close()
                rools[symbol+"USDT"] = True
                f = open(main_path_settings, "w")
                json.dump(rools, f)
                f.close()

                return ["danger"]
            else:
                main_path_settings = f'/usr/local/WB/dashboard/data/settings.json'

                a_file1 = open(main_path_settings, "r")
                rools = json.load(a_file1)
                a_file1.close()
                rools[symbol+"USDT"] = False
                f = open(main_path_settings, "w")
                json.dump(rools, f)
                f.close()
                return ["success"]
        else:
            raise PreventUpdate


@dash_app.callback(
    [Output("start_btn", 'children'),
     Output("start_btn", 'color')],
    [Input("start_btn", 'n_clicks')]
)
def toggle_modal_main(n1):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')

    if button_id[0] == 'start_btn':
        main_path_settings = f'/usr/local/WB/dashboard/data/active.json'
        a_file1 = open(main_path_settings, "r")
        rools = json.load(a_file1)
        a_file1.close()

        if not rools['active']:
            pid = subprocess.Popen(["python", "/usr/local/WB/dashboard/my_class/combo.py"]).pid
            rools['active'] = pid
            f = open(main_path_settings, "w")
            json.dump(rools, f)
            f.close()
            return ["STOP", "danger"]
        else:
            pidid = rools['active']
            rools['active'] = False
            f = open(main_path_settings, "w")
            json.dump(rools, f)
            f.close()
            os.kill(int(pidid), signal.SIGKILL)
            return ["START", "success"]
    else:
        raise PreventUpdate


if __name__ == '__main__':
    dash_app.run_server(host="0.0.0.0", port=5033, debug=False)
