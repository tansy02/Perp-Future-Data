#mainet: https://api.hyperliquid.xyz
#testnet: https://api.hyperliquid-testnet.xyz

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
from hyperliquid.info import Info
from hyperliquid.utils import constants
from hyperliquid.exchange import Exchange
from eth_account import Account
import csv
from datetime import datetime
import time

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

def date_to_milliseconds(date_str):  #convert into the format the api takes
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(dt.timetuple()) * 1000)

start = date_to_milliseconds("2025-05-05 00:00:00")#no need start time just end time is cool
end = date_to_milliseconds("2025-05-10 06:00:00") #note this date is based on the api's default date
#date returned via the dataframe is the date synced with your computer's timezone

def data_extraction_past(symbol,interval_1,interval_2,end,limit):
    end = date_to_milliseconds(end)
    url = "https://api.binance.com/api/v3/klines"
    params_1m = {
        "symbol": symbol,
        "interval": interval_1,
        "endTime": end,
        "limit" : limit
    }

    resp = requests.get(url, params=params_1m)
    data_1m = resp.json()

    price_1m = pd.DataFrame(data_1m, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote"
    ])

    price_1m["Open Time"] = pd.to_datetime(price_1m["Open Time"], unit="ms")
    price_1m = price_1m[["Open Time", "Open", "High", "Low", "Close", "Volume"]]
    #print(price_1m)
    #convert df to list
    open_1m = price_1m["Open"].values.tolist()
    close_1m = price_1m["Close"].values.tolist()
    #convert str to float in list
    open_1m = list(map(float,open_1m))
    close_1m = list(map(float,close_1m))
    close_avg_1m = sum(close_1m)/len(close_1m)

    params_5m = {
        "symbol": symbol,
        "interval": interval_2,
        "endTime": end,
        "limit": limit # up to 1000
    }

    resp = requests.get(url, params=params_5m)
    data_5m = resp.json()

    price_5m = pd.DataFrame(data_5m, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote"
    ])

    price_5m["Open Time"] = pd.to_datetime(price_5m["Open Time"], unit="ms")
    price_5m = price_5m[["Open Time", "Open", "High", "Low", "Close", "Volume"]]
    #print(price_5m)

    #convert df to list
    open_5m = price_5m["Close"].values.tolist()
    close_5m = price_5m["Open"].values.tolist()
    volume_5m = price_5m["Volume"].values.tolist()

    #convert str to float
    open_5m = list(map(float,open_5m))
    close_5m = list(map(float,close_5m))
    volume_5m = list(map(float,volume_5m))

    siu = len(close_5m) - 1
    final_close_price = close_5m[siu] #for later when calculating percentage change

    volume_avg = sum(volume_5m)/len(volume_5m)
    close_avg_5m = sum(close_5m)/len(close_5m) 
    close_co = correlation(close_5m, close_1m)
    open_co = correlation(open_5m, open_1m)
    #print("Closing Correlation" , close_co)
    #print("Opening Correlation", open_co)


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
        #print(f"Formula: y= {a:.2f}x + {b:.2f}")
        is_linear = True

    else:
        #print(f"Formula: y = {a:.2f}x² + {b:.2f}x + {c:.2f}")
        is_linear = False

    #let dependent variable be the avg closing price for the next 3 '5m' candles
    params_5m = {
    "symbol": symbol,
    "interval": interval_2,
    "startTime": end,
    "limit": 3 # up to 1000
    }

    resp = requests.get(url, params=params_5m)
    data_5m = resp.json()

    price_5m = pd.DataFrame(data_5m, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote"
    ])

    close_5m = price_5m["Close"].values.tolist()
    close_5m = list(map(float,close_5m))
    y = sum(close_5m)/len(close_5m)

    #express the price in terms of percentage changes
    percentage_change = (y - final_close_price)/final_close_price

    #append new data to csv
    end_datetime = price_1m["Open Time"][99]
    new_data = [end_datetime,a,is_linear, open_co,close_co,close_avg_1m, close_avg_5m,volume_avg, percentage_change]
    file_path = r"C:\Leisure\Data Analyst shit\Trading\data.csv"
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        #append the data
        writer.writerow(new_data)


#tis function need to be updated as per the one above
def data_extraction_present(symbol, interval_1,interval_2,limit):
    url = "https://api.binance.com/api/v3/klines"
    params_1m = {
        "symbol": symbol,
        "interval": interval_1,
        "limit": limit  # up to 1000
    }

    resp = requests.get(url, params=params_1m)
    data_1m = resp.json()

    price_1m = pd.DataFrame(data_1m, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote"
    ])

    price_1m["Open Time"] = pd.to_datetime(price_1m["Open Time"], unit="ms")
    price_1m = price_1m[["Open Time", "Open", "High", "Low", "Close", "Volume"]]
    #print(price_1m)
    #convert df to list
    open_1m = price_1m["Open"].values.tolist()
    close_1m = price_1m["Close"].values.tolist()
    #convert str to float in list
    open_1m = list(map(float,open_1m))
    close_1m = list(map(float,close_1m))

    params_5m = {
        "symbol": symbol,
        "interval": interval_2,
        "limit": limit  # up to 1000
    }

    resp = requests.get(url, params=params_5m)
    data_5m = resp.json()

    price_5m = pd.DataFrame(data_5m, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote"
    ])

    price_5m["Open Time"] = pd.to_datetime(price_5m["Open Time"], unit="ms")
    price_5m = price_5m[["Open Time", "Open", "High", "Low", "Close", "Volume"]]
    #print(price_5m)

    #convert df to list
    open_5m = price_5m["Close"].values.tolist()
    close_5m = price_5m["Open"].values.tolist()

    #convert str to float
    open_5m = list(map(float,open_5m))
    close_5m = list(map(float,close_5m))


    close_co = correlation(close_5m, close_1m)
    open_co = correlation(open_5m, open_1m)
    #print("Closing Correlation" , close_co)
    #print("Opening Correlation", open_co)


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
    new_data = [datetime.now(),a,is_linear, open_co,close_co]
    file_path = r"C:\Leisure\Data Analyst shit\Trading\data.csv"

    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        #append the data
        writer.writerow(new_data)

        
def MA(list1, factor):
    list2 = []
    ans = []
    for i in range(len(list1)):
        for i in range(factor):
            list2.append(list1[i+factor])
        
        a = sum(list2)/factor
        ans.append(a)
        list2 =[]
    return ans
            
    