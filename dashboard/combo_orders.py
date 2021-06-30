import time
import sys
import os
import requests
import argparse
sys.path.insert(0, r'/usr/local/WB/dashboard')
import dbrools



parser = argparse.ArgumentParser()
parser.add_argument('--symbol', help='bnb or link')
parser.add_argument('--amount', help='Amount')
args = parser.parse_args()




