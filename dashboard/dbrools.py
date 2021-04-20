from pymongo import MongoClient, ASCENDING, DESCENDING

# client = MongoClient('mongodb://137.220.59.5:51125')
client = MongoClient('mongodb_defi', 27017)
db = client['DeFi']
my_data = db['Data']
my_bal = db['Balance']
my_history = db['History']
my_active = db['Active']

full_data = db['DataFull']


def clean():
    my_data.remove({})
    insert_document(my_data, {"sku": 1, "data": {}})


def insert_document(collection, data):
    return collection.insert_one(data).inserted_id


def update_document(collection, data, query):
    myquery = {"sku": query}
    newvalues = {"$set": {"sku": 1, "data": data}}
    return collection.update_one(myquery, newvalues)


def update_main_data(data=None):
    if not data:
        data = {
            "sku": 1,
            "data": {}
        }
    update_document(my_data, data, 1)
    return


def update_full_data(data=None):
    if not data:
        data = {
            "sku": 1,
            "data": {}
        }
    update_document(full_data, data, 1)
    return


def get_my_data():
    d = {}
    for i in my_data.find():
        d.update(i)
    return d


def get_full_data():
    d = {}
    for i in full_data.find():
        d.update(i)
    return d


# -------- BALANCE  ----------
def insert_new_balances(data, usdt):
    myquery = {"sku": 1}
    my_bal.update(myquery, {"$set": {'Balances': data}})
    my_bal.update(myquery, {"$set": {'Free': usdt}})
    return


def get_my_balances():
    d = {}
    for i in my_bal.find():
        d.update(i)
        break
    return d


def inc_locked_balances(usdt):
    myquery = {"sku": 1}
    my_bal.update(myquery, {"$inc": {'Locked': usdt}})
    return


def minus_locked_balances(usdt):
    myquery = {"sku": 1}
    my_bal.update(myquery, {"$inc": {'Locked': usdt}})
    return


# -------- HISTORY  ----------
def get_history_data():

    d = []

    for i in my_history.find():
        d.append(i)
    return d


def insert_history(data=None):
    insert_document(my_history, data)
    return


def update_balances(symbol, data):
    myquery = {"sku": 1}
    my_bal.update(myquery, {"$set": {f'{symbol}': data}})
    return


def create_balance():
    data = {
        "sku": 1,
        "USDT": 0,
        "ETHUP": 0,
        "ETH": 0,
    }
    insert_document(my_bal, data)
    return


def create_full_data():
    data = {
        "sku": 1,
        "data": {}
    }
    insert_document(full_data, data)
    return


def create_active():
    symbols = ["XRP", "BTC", "ETH",
               "TRX", "EOS", "BNB",
               "LINK", "FIL", "YFI",
               "DOT", "SXP", "UNI",
               "LTC", "ADA", "AAVE"]

    for i in symbols:
        for k in ['buy', 'sell']:
            data = {
                "symbol": i,
                "side": k,
                "amount": 0,
                "process": 0
            }
            insert_document(my_active, data)
    return


def get_active_data():

    d = []

    for i in my_active.find():
        d.append(i)
    return d

# create_full_data()
# create_balance()
# print(get_my_balances())
# d = get_full_data()
# print(d["data"]["ETHUSDT"])