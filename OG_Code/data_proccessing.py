#mainet: https://api.hyperliquid.xyz
#testnet: https://api.hyperliquid-testnet.xyz

import pandas as pd
import numpy as np
import requests # FIX: removed unused imports (matplotlib, hyperliquid x3, eth_account)
import csv
import datetime


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


#GRAPH PLOTTING TIME or FORMULA DEDUCTION TIME
#TO SMOOTHEN THE DATA ACROSS VARYING PRICES, WE EXPRESS IT AS A PERCENTAGE *10000(NOT DECIMALS) OF ITS 1ST DATA POINT
a = open_1m[0]
open_1m = [(i / a)*100000 for i in open_1m] #multiply by 100,000 as the coefficient is too small.

time_axis = list(range(1, len(open_5m)+1)) #[1,2,3...100]
open_1m = np.array(open_1m) #the list has double [[ dk why
close_1m = np.array(close_1m)

open_5m = np.array(open_5m)
close_5m = np.array(close_5m)

#Polynomial Fit
coeffs = np.polyfit(time_axis, open_1m, deg=2)
a, b, c = coeffs
if a < 0.001:  #Linear Fit, a is x^2 coefficient   
    coeffs = np.polyfit(time_axis, open_1m, deg =1)
    a, b = coeffs
    print(f"Formula: y= {a:.2f}x + {b:.2f}")
    is_linear = True

else:
    print(f"Formula: y = {a:.2f}x² + {b:.2f}x + {c:.2f}")
    is_linear = False

#append new data to csv
new_data = [datetime.datetime.now(),a,is_linear, open_co,close_co]
file_path = "data.csv"
with open(file_path, mode='a', newline='') as file:
    writer = csv.writer(file)
    
    #append the data
    writer.writerow(new_data)

#Custom function fit

#TO SMOOTHEN THE DATA, WE EXPRESS IT AS A PERCENTAGE OF ITS 1ST DATA POINT