import time
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--symbol', help='bnb or link')
parser.add_argument('--side', help='sell or buy')
parser.add_argument('--amount', help='Amount')
args = parser.parse_args()


print((args.symbol, float(args.amount), args.side))
n = 0
while n < 50:
    n += 1
    print(n)
    time.sleep(5)
