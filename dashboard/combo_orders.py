import argparse
import Orders
import logging
import json

parser = argparse.ArgumentParser()
parser.add_argument('--symbol', help='bnbusdt or linkusdt')
parser.add_argument('--amount', help='Amount')
parser.add_argument('--decimalsp', help='1 or 2')
parser.add_argument('--decimals', help='1 or 2')
parser.add_argument('--main_direction', help='1 or 2')
parser.add_argument('--my_sl', help='sl price')
parser.add_argument('--my_tp', help='tp price')

args = parser.parse_args()


reponse_tp = Orders.tp_future(symbol=args.symbol,
                              side=int(args.main_direction),
                              price=str(round(float(args.my_tp), args.decimalsp)),
                              amount=round(float(args.amount), args.decimals))
if reponse_tp['error']:
    logging.info(f"TP order Error:\n {reponse_tp}")
    order_id_tp = False
else:
    order_id_tp = reponse_tp['result']['clientOrderId']
    logging.info(f"added TP order : {args.symbol}")

reponse_sl = Orders.sl_future(symbol=args.symbol,
                              side=int(args.main_direction),
                              price=str(round(float(args.my_sl), args.decimalsp)),
                              amount=round(float(args.amount), args.decimals))
if reponse_sl['error']:
    logging.info(f"TP order Error:\n {reponse_sl}")
    order_id_sl = False
else:
    order_id_sl = reponse_sl['result']['clientOrderId']
    logging.info(f"added SL order : {args.symbol}")

new_data = {
    "tp": order_id_tp,
    "sl": order_id_sl
}

main_path = f'/usr/local/WB/dashboard/orders/{args.symbol}.json'

with open(main_path, 'w', encoding='utf-8') as outfile:
    json.dump(new_data, outfile, ensure_ascii=False, indent=4)
