import argparse
import Orders
import logging
import json

parser = argparse.ArgumentParser()
parser.add_argument('--symbol', help='bnbusdt')
parser.add_argument('--my_profitf', help='0.258')
args = parser.parse_args()


main_path = f'/usr/local/WB/dashboard/orders/{args.symbol}.json'

with open(main_path, 'r') as outfile:
    data = json.load(outfile)
    if float(args.my_profitf) > 0:
        bot_message = f"canceled SL order id:\n {data['sl']}"
        Orders.cancel_my_order(symbol=args.symbol, my_id=data['sl'])
        logging.info(bot_message)
        print("\n", bot_message)
    else:
        bot_message = f"canceled TP order id:\n {data['tp']}"
        Orders.cancel_my_order(symbol=args.symbol, my_id=data['tp'])
        logging.info(bot_message)
        print("\n", bot_message)

