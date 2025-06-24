#mainet: https://api.hyperliquid.xyz
#testnet: https://api.hyperliquid-testnet.xyz

import pandas as pd
import requests
from hyperliquid.info import Info
from hyperliquid.utils import constants
from hyperliquid.exchange import Exchange
from eth_account import Account

def correlation(x,y):
    mean_x = sum(x)/len(x)
    mean_y = sum(y)/len(y)

    #numerator portion of formula
    
    numerator = []
    for i in range (len(x)-1):
        a = x[i] - mean_x
        b = y[i] - mean_y
        c = a*b 
        numerator.append(c)
    numerator = sum(numerator)

    #denominator portion of formula
    denominator = []
    sum_1 = []
    sum_2 = []
    for i in range (len(x)-1):
        a = x[i] - mean_x
        b = y[i] - mean_y
        a = a*a
        b = b*b
        sum_1.append(a) #even indexes
        sum_2.append(b) #odd indexes

    sum_1 = sum(sum_1)
    sum_2 = sum(sum_2)
    denominator = ((sum_1*sum_2) **(1/2)) #square root whole thing

    ans = numerator/denominator
    return ans


#the config.json is linked to hyperliquid's orders and private keys executions

Test_net_endpoint = "https://api.hyperliquid-testnet.xyz"
info = Info(constants.TESTNET_API_URL, skip_ws=True)

priv_key = "0x..."
API_address = "0xdCC9Eb04DFF815f9C0Bac4ddA7309b736Baa691F"


user_state = info.user_state("0xD19A603F9a7c5404A52e79D0dfc40db90135d7c5")
print(user_state)

""" #pull meta data
meta = info.meta()
universes = meta["universe"]
#convert to df
df = pd.DataFrame(universes)
print(df)
#neatening or renaming the things lol
column_map = {
    "name": "symbol",
    "szDecimals": "size_decimals",
    "maxLeverage": "max_leverage",
    "onlyIsolated": "isolated_only"
}
df = df.rename(columns = column_map)
wanted_cols = ["symbol", "size_decimals", "max_leverage", "isolated_only"]
df = df[wanted_cols].sort_values("symbol").reset_index(drop=True)

print(df)"""

#data extraction from binance

url = "https://api.binance.com/api/v3/klines"
params_1m = {
    "symbol": "BTCUSDT",
    "interval": "1m",
    "limit": 100  # up to 1000
}

resp = requests.get(url, params=params_1m)
data_1m = resp.json()

price_1m = pd.DataFrame(data_1m, columns=[
    "Open Time", "Open", "High", "Low", "Close", "Volume",
    "Close Time", "Quote Asset Volume", "Trades",
    "Taker Buy Base", "Taker Buy Quote", "Ignore"
])

price_1m["Open Time"] = pd.to_datetime(price_1m["Open Time"], unit="ms")
price_1m = price_1m[["Open Time", "Open", "High", "Low", "Close", "Volume"]]
print(price_1m)
#convert df to list
open_1m = price_1m["Open"].values.tolist()
close_1m = price_1m["Close"].values.tolist()
#convert str to float in list
open_1m = list(map(float,open_1m))
close_1m = list(map(float,close_1m))

params_5m = {
    "symbol": "BTCUSDT",
    "interval": "5m",
    "limit": 100  # up to 1000
}

resp = requests.get(url, params=params_5m)
data_5m = resp.json()

price_5m = pd.DataFrame(data_5m, columns=[
    "Open Time", "Open", "High", "Low", "Close", "Volume",
    "Close Time", "Quote Asset Volume", "Trades",
    "Taker Buy Base", "Taker Buy Quote", "Ignore"
])

price_5m["Open Time"] = pd.to_datetime(price_5m["Open Time"], unit="ms")
price_5m = price_5m[["Open Time", "Open", "High", "Low", "Close", "Volume"]]
print(price_5m)

#convert df to list
open_5m = price_5m["Close"].values.tolist()
close_5m = price_5m["Open"].values.tolist()

#convert str to float
open_5m = list(map(float,open_5m))
close_5m = list(map(float,close_5m))


close_co = correlation(close_5m, close_1m)
open_co = correlation(open_5m, open_1m)
print("Closing Correlation" , close_co)
print("Opening Correlation", open_co)



#To allow machine to execute another order once one is filled can use a while loop
#orders commands
wallet = Account.from_key(priv_key)
exchange = Exchange(wallet = wallet, account_address = API_address, base_url = Test_net_endpoint )
#by default endpoint is main_net

#market order
coin = "ETH"
is_buy = True
sz = 0.05

siu = exchange.market_open(coin, is_buy, sz, None, 0.01)  #last variable stands for slippage
if siu["status"] == "ok":
    print("filled")


#limit order
px = 2500
limit = exchange.order(coin, is_buy, sz, 2500, {"limit": {"tif":"Gtc"}})
print(limit )

# Query the order status by oid
if limit["status"] == "ok":
    status = limit["response"]["data"]["statuses"][0]
    if "resting" in status:
        order_status = info.query_order_by_oid(API_address, status["resting"]["oid"])
        print("Order status by oid:", order_status)

# Cancel the order
"""if limit["status"] == "ok":
    status = limit["response"]["data"]["statuses"][0]
    if "resting" in status:
        cancel_result = exchange.cancel("ETH", status["resting"]["oid"])
        print(cancel_result)"""
        