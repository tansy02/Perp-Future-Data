#mainet: https://api.hyperliquid.xyz
#testnet: https://api.hyperliquid-testnet.xyz

import pandas as pd
import requests
from hyperliquid.info import Info
from hyperliquid.utils import constants
from hyperliquid.exchange import Exchange
from eth_account import Account


Test_net_endpoint = "https://api.hyperliquid-testnet.xyz"
info = Info(constants.TESTNET_API_URL, skip_ws=True)

priv_key = "0x..."
pub_key = "0x..."


user_state = info.user_state(pub_key)
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
params = {
    "symbol": "BTCUSDT",
    "interval": "1m",
    "limit": 100  # up to 1000
}

resp = requests.get(url, params=params)
data = resp.json()

df = pd.DataFrame(data, columns=[
    "Open Time", "Open", "High", "Low", "Close", "Volume",
    "Close Time", "Quote Asset Volume", "Trades",
    "Taker Buy Base", "Taker Buy Quote", "Ignore"
])

df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
df = df[["Open Time", "Open", "High", "Low", "Close", "Volume"]]
print(df)


#To allow machine to execute another order once one is filled can use a while loop
#orders commands
wallet = Account.from_key(priv_key)
exchange = Exchange(wallet = wallet, account_address = pub_key, base_url = Test_net_endpoint )


coin = "ETH"
is_buy = True
sz = 0.05

siu = exchange.market_open(coin, is_buy, sz, None, 0.01)  #last variable stands for slippage
if siu["status"] == "ok":
    print("filled")


