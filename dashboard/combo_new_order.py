import argparse
import Orders
import logging

parser = argparse.ArgumentParser()
parser.add_argument('--symbol', help='bnbusdt or linkusdt')
parser.add_argument('--amount', help='Amount')
parser.add_argument('--decimals', help='decimals')
parser.add_argument('--main_direction', help='1 or 2')


args = parser.parse_args()

reponse = Orders.my_order_future(symbol=args.symbol,
                                 side=int(args.main_direction),
                                 amount=round(float(args.amount), int(args.decimals)))

if reponse['error']:
    logging.info(f"New order Error:\n {reponse}")
else:
    logging.info(f"New order:\n {reponse}")
