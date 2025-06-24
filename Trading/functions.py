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
import random

import sqlite3


dt = "2023-10-10 06:00:00"
def date_to_milliseconds(date_str):  #convert into the format the api takes
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(dt.timetuple()) * 1000)

def convert_float(DataFrame):
    for col in DataFrame.columns:
        DataFrame[col] = DataFrame[col].astype(float)


def data_extraction_past_v2(symbol,interval_1,interval_2,start_time1,start_time2,limit):
    start_time1 = date_to_milliseconds(start_time1)
    start_time2 = date_to_milliseconds(start_time2)
    url = "https://api.binance.com/api/v3/klines"
    params_1m = {
        "symbol": symbol,
        "interval": interval_1,
        "startTime": start_time1,
        "limit":limit
    }

    resp = requests.get(url, params=params_1m)
    data_1m = resp.json()
    #print(data_1m)
    price_1m = pd.DataFrame(data_1m, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote","Ignore"
    ])


    #convert str to float
    convert_float(price_1m)

    price_1m = price_1m.values.tolist() #this format is required to append to csv.

    #end_1m to be used in predicting data
    siu = len(price_1m) -1
    end_1m = price_1m[siu][0] #returns the latest time frame
    last_close_1m = price_1m[siu][4]
    last_close_1m =float(last_close_1m)

    #print(end_1m)

    
    params_5m = {
        "symbol": symbol,
        "interval": interval_2,
        "startTime":start_time2,
        "limit":limit
    }

    resp = requests.get(url, params=params_5m)
    data_5m = resp.json()

    price_5m = pd.DataFrame(data_5m, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote", "Ignore"
    ])

    #convert str to float
    convert_float(price_5m)

    #convert df to list
    price_5m = price_5m.values.tolist()

    #Time frame returning time
    siu = len(price_5m) -1
    end_5m = price_5m[siu][0]
    last_close_5m = price_5m[siu][4]
    last_close_5m =float(last_close_5m)

    #print(end_5m, 'end_5m')
    params_1m = {
        "symbol": symbol,
        "interval": interval_1,
        "startTime": int(end_1m), #cannot process float must be int
        "limit": 3
    }
    resp = requests.get(url, params = params_1m)
    data_1m = resp.json()

    data_1m = pd.DataFrame(data_5m, columns = [
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote", "Ignore"])
    
    close_1m = data_1m["Close"].values.tolist()
    close_1m = list(map(float,close_1m))
    y_1m = sum(close_1m)/len(close_1m)
    
    #let dependent variable be the avg closing price for the next 3 '5m' candles
    params_5m = {
    "symbol": symbol,
    "interval": interval_2,
    "startTime": int(end_5m), #cannot process float must be int
    "limit": 3 # up to 1000
    }

    resp = requests.get(url, params=params_5m)
    data_5m = resp.json()

    data_5m = pd.DataFrame(data_5m, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote", "Ignore"
    ])


    close_5m = data_5m["Close"].values.tolist()
    close_5m = list(map(float,close_5m))
    y_5m = sum(close_5m)/len(close_5m)


    new_data = []
    
    #1m append
    for i in range(len(price_1m[0])):
    
        for c in range(len(price_1m)):
            new_data.append(price_1m[c][i])

    
    #print(new_data, "siu")
    new_data.append(y_1m)
    new_data.append(last_close_1m)
  
    file_path = r"C:\Leisure\Data Analyst shit\Trading\data_1m.csv"
    with open(file_path, mode = 'a', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(new_data)

    #5m append

    new_data = []
    

    for i in range(len(price_5m[0])):

        for c in range(len(price_5m)):
            new_data.append(price_5m[c][i])

    
    #print(new_data, "siu")
    new_data.append(y_5m)
    new_data.append(last_close_5m)
    file_path = r"C:\Leisure\Data Analyst shit\Trading\data_5m.csv"
    with open(file_path, mode = 'a', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(new_data)

    #append new data to csv (1m), scrap this loop, CREATES MULTIPLE ROWS AGAINST 1 Y VALUE IN CSV.

    """    
    for i in range(len(price_1m)):
        new_data = [price_1m[i]]

        
        file_path = r"C:\Leisure\Data Analyst shit\Trading\data_1m.csv"
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
                
                #append the data
            writer.writerow(new_data)

    for i in range(len(price_5m)):
        new_data = [price_5m[i]]

        file_path = r"C:\Leisure\Data Analyst shit\Trading\data_5m.csv"
        with open(file_path,mode = 'a', newline = '') as file:
            writre = csv.writer(file)
            writer.writerow(new_data)
"""
def zero_infront(value): #change '6' to '06', etc
    if value < 10:
        value = "0" + str(value)
    else:
        value = str(value)
    return value


year = random.randint(2015,2025)
year = str(year)

month = random.randint(1,12)
if month != 2:
    if month in [1,3,5,7,8,10,12]:
        day = random.randint(1,31)
    else:
        day = random.randint(1,30)
else:
    day = random.randint(1,28)


time_ = random.randint(0,23)
time_ = zero_infront(time_) #for immutable types such as int, str, etc the function cannot change the variable beyond the function
month = zero_infront(month)
day = zero_infront(day)

print(time_)


end_time = year + "-" + month + "-" + day + " " + time_ + ":00:00"
print(end_time)

#data_extraction_past_v2("BTCUSDT", '1m','5m',end_time,end_time)
def weight_calculator_csv(data_types, csv_file_path):
    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file)
        headers = next(reader)

    headers.append('Ignore') #added to fix the while loop 
    weight_ea = 1.0/len(data_types)
    weight = []
    c = 0
    for i in range(len(data_types)):
        count = 0
        try:

            while data_types[i] in headers[c]:
                count += 1
                c += 1
        except(IndexError):
            continue

        for abc in range(count):
            weight.append(weight_ea/count)

    return weight

def weight_calculator(data_types, headers):

    headers.append('Ignore') #added to fix the while loop 
    weight_ea = 1.0/len(data_types)
    weight = []
    c = 0
    for i in range(len(data_types)):
        count = 0
        try:

            while data_types[i] in headers[c]:
                count += 1
                c += 1
        except(IndexError):
            continue

        for abc in range(count):
            weight.append(weight_ea/count)

    headers.remove('Ignore')
    return weight



def data_extraction_past_v3(symbol,interval_1,interval_2,start_time1,start_time2,limit,headers):
    start_time1 = date_to_milliseconds(start_time1)
    start_time2 = date_to_milliseconds(start_time2)
    url = "https://api.binance.com/api/v3/klines"
    params_1m = {
        "symbol": symbol,
        "interval": interval_1,
        "startTime": start_time1,
        "limit":limit
    }

    resp = requests.get(url, params=params_1m)
    data_1m = resp.json()
    #print(data_1m)
    price_1m = pd.DataFrame(data_1m, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote", "Ignore"
    ])
    price_1m = price_1m.drop('Ignore', axis = 1) #DROP THE IGNORE CUZ ITS A NUISANCE TO BE IGNORED

    #convert str to float
    convert_float(price_1m)

    price_1m = price_1m.values.tolist() #this format is required to append to csv.

    #end_1m to be used in predicting data
    siu = len(price_1m) -1
    end_1m = price_1m[siu][0] #returns the latest time frame
    last_close_1m = price_1m[siu][4]
    last_close_1m =float(last_close_1m)

    #print(end_1m)

    
    params_5m = {
        "symbol": symbol,
        "interval": interval_2,
        "startTime":start_time2,
        "limit":limit
    }

    resp = requests.get(url, params=params_5m)
    data_5m = resp.json()

    price_5m = pd.DataFrame(data_5m, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote", "Ignore"
    ])
    price_5m = price_5m.drop('Ignore', axis = 1) #DROP THE IGNORE CUZ ITS A NUISANCE TO BE IGNORED

    #convert str to float
    convert_float(price_5m)

    #convert df to list
    price_5m = price_5m.values.tolist()

    #Time frame returning time
    siu = len(price_5m) -1
    end_5m = price_5m[siu][0]
    last_close_5m = price_5m[siu][4]
    last_close_5m =float(last_close_5m)

    #print(end_5m, 'end_5m')
    params_1m = {
        "symbol": symbol,
        "interval": interval_1,
        "startTime": int(end_1m), #cannot process float must be int
        "limit": 3
    }
    resp = requests.get(url, params = params_1m)
    data_1m = resp.json()

    data_1m = pd.DataFrame(data_5m, columns = [
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote","Ignore"])
    
    close_1m = data_1m["Close"].values.tolist()
    close_1m = list(map(float,close_1m))
    y_1m = sum(close_1m)/len(close_1m)
    
    #let dependent variable be the avg closing price for the next 3 '5m' candles
    params_5m = {
    "symbol": symbol,
    "interval": interval_2,
    "startTime": int(end_5m), #cannot process float must be int
    "limit": 3 # up to 1000
    }

    resp = requests.get(url, params=params_5m)
    data_5m = resp.json()

    data_5m = pd.DataFrame(data_5m, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote","Ignore"
    ])


    close_5m = data_5m["Close"].values.tolist()
    close_5m = list(map(float,close_5m))
    y_5m = sum(close_5m)/len(close_5m)


    new_data = []

    #1m append
    for i in range(len(price_1m[0])):
    
        for c in range(len(price_1m)):
            new_data.append(price_1m[c][i])

    #print(new_data, "siu")
    new_data.append(y_1m)
    new_data.append(last_close_1m)

    #connect 
    conn = sqlite3.connect("data_1m.db")
    cursor = conn.cursor()

    #placeholder generation
    placeholders = ", ".join(["?"]*len(headers)) #creating a bunch of (?,?,?...?) as placeholders

    #append data
    cursor.execute(f"INSERT INTO my_table VALUES ({placeholders})", new_data)
    conn.commit() #COMMIT THE CHANGES AKA SAVE THE CHANGES
    cursor.close() #CLOSE CURSOR WHEN DONE
    conn.close()  #CLOSE CONNECTION WHEN DONE


    new_data = []
    

    for i in range(len(price_5m[0])):

        for c in range(len(price_5m)):
            new_data.append(price_5m[c][i])


    #print(new_data, "siu")
    new_data.append(y_5m)
    new_data.append(last_close_5m)


    #connect 
    conn = sqlite3.connect("data_5m.db")
    cursor = conn.cursor()

    #placeholder generation
    placeholders = ", ".join(["?"]*len(headers))

    #append data
    cursor.execute(f"INSERT INTO my_table VALUES ({placeholders})", new_data) 
    conn.commit() #COMMIT THE CHANGES AKA SAVE THE CHANGES
    cursor.close() #CLOSE CURSOR WHEN DONE
    conn.close()  #CLOSE CONNECTION WHEN DONE