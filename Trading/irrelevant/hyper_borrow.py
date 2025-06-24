import requests

url = "https://api.hyperlend.finance/data/markets?chain=hyperEvm"
params_1m = {
    "symbol": "BTCUSDT",
    "interval": "1m",
    "limit": 100  # up to 1000
}

resp = requests.get(url)
data = resp.json()

debt = [reserve["totalScaledVariableDebt"] for reserve in data["reserves"]]
index = [reserve["variableBorrowIndex"] for reserve in data["reserves"]]
debt = list(map(float,debt))
index = list(map(float,index))
print(debt)
print(index)
