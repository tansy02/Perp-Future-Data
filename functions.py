import pandas as pd
import requests
from datetime import datetime
import time

import sqlite3


#Binance USD-M futures endpoint (BTCUSDT perpetual). The spot endpoint is api.binance.com/api/v3/klines
url = "https://fapi.binance.com/fapi/v1/klines"

kline_columns = [
    "Open Time", "Open", "High", "Low", "Close", "Volume",
    "Close Time", "Quote Asset Volume", "Trades",
    "Taker Buy Base", "Taker Buy Quote", "Ignore"
]


def date_to_milliseconds(date_str):  #convert into the format the api takes
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(dt.timetuple()) * 1000)

def convert_float(DataFrame):
    for col in DataFrame.columns:
        DataFrame[col] = DataFrame[col].astype(float)


def zero_infront(value): #change '6' to '06', etc
    if value < 10:
        value = "0" + str(value)
    else:
        value = str(value)
    return value


def get_klines(symbol, interval, start_time, limit):
    #one request to binance, returns a dataframe of floats without the 'Ignore' column
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": int(start_time), #cannot process float must be int
        "limit": limit
    }
    resp = requests.get(url, params=params)
    data = resp.json()

    #binance returns a dict like {"code": -1121, "msg": ...} on errors, which would not fit the columns
    if not isinstance(data, list):
        raise ValueError(f"Binance error: {data}")

    df = pd.DataFrame(data, columns=kline_columns)
    df = df.drop('Ignore', axis = 1) #DROP THE IGNORE CUZ ITS A NUISANCE TO BE IGNORED
    convert_float(df)
    return df


def build_row(symbol, interval, start_time, limit, horizon):
    #features = 'limit' candles starting at start_time
    #y        = avg close of the next 'horizon' candles AFTER the last feature candle (no overlap with the features)
    price = get_klines(symbol, interval, start_time, limit)

    #if binance returns fewer candles than asked (eg end of data) the row would not fit the table
    if len(price) != limit:
        raise IndexError("not enough candles returned")

    price = price.values.tolist() #this format is required to append to the DB

    siu = len(price) -1
    last_close = float(price[siu][4])
    last_close_time = price[siu][6] #Close Time of the last feature candle

    #label window starts 1ms after the last feature candle closes, so it is strictly in the future
    future = get_klines(symbol, interval, last_close_time + 1, horizon)
    if len(future) != horizon:
        raise IndexError("not enough future candles returned")

    close = future["Close"].values.tolist()
    y = sum(close)/len(close)

    new_data = []
    #stored column by column: Open Time0..19, Open0..19, ... to match the headers
    for i in range(len(price[0])):
        for c in range(len(price)):
            new_data.append(price[c][i])

    new_data.append(y)
    new_data.append(last_close)
    return new_data


def insert_row(db_path, new_data, headers):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #placeholder generation
    placeholders = ", ".join(["?"]*len(headers)) #creating a bunch of (?,?,?...?) as placeholders

    #append data
    cursor.execute(f"INSERT INTO my_table VALUES ({placeholders})", new_data)
    conn.commit() #COMMIT THE CHANGES AKA SAVE THE CHANGES
    cursor.close() #CLOSE CURSOR WHEN DONE
    conn.close()  #CLOSE CONNECTION WHEN DONE


def data_extraction_past_v3(symbol,interval_1,interval_2,start_time1,start_time2,limit,headers, horizon = 3):
    start_time1 = date_to_milliseconds(start_time1)
    start_time2 = date_to_milliseconds(start_time2)

    #let dependent variable be the avg closing price of the next 3 candles after the feature window
    row_1m = build_row(symbol, interval_1, start_time1, limit, horizon)
    row_5m = build_row(symbol, interval_2, start_time2, limit, horizon)

    #only insert once both rows are fetched, so the two DBs stay in step
    insert_row("data_1m.db", row_1m, headers)
    insert_row("data_5m.db", row_5m, headers)


#feature families used by the classifiers. Open Time / Close Time are left out on purpose:
#they are timestamps, so a model could learn the date instead of the price action
price_types = ["Open", "High", "Low", "Close"]
volume_types = ["Volume", "Quote Asset Volume", "Trades", "Taker Buy Base", "Taker Buy Quote"]
feature_types = price_types + volume_types


def family_columns(data_type, limit = 20):
    return [data_type + str(c) for c in range(limit)]


def load_data(db_path, limit = 20):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM my_table", conn)
    conn.close()

    #cleaning: values are stored as TEXT, so convert, then drop duplicate and broken rows
    df = df.drop_duplicates()
    df = df.apply(pd.to_numeric, errors = 'coerce')
    df = df.dropna().reset_index(drop = True)

    y = (df['y'] > df['last_close']).astype(int) #1 = avg of next candles closes above the last close

    #BTC went from ~7k to ~100k over the sample, so raw prices mostly tell the model which year it is.
    #prices -> % distance from the last close, volumes -> relative to that window's own average
    parts = []
    for data_type in price_types:
        cols = family_columns(data_type, limit)
        parts.append(df[cols].div(df['last_close'], axis = 0) - 1)
    for data_type in volume_types:
        cols = family_columns(data_type, limit)
        parts.append(df[cols].div(df[cols].mean(axis = 1) + 1e-12, axis = 0))
    X = pd.concat(parts, axis = 1) #join once at the end, adding columns one by one is slow in pandas

    return X, y
