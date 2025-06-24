import yfinance as yf
import pandas as pd
import numpy as np
import math 

#CORRELATION #
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

#Multiple Correlation
def multi_correlation(x,y,z):

    r_xy = correlation(x,y)
    r_xy2 = r_xy**2

    r_xz = correlation(x,z)
    r_xz2 = r_xz**2

    r_yz = correlation(y,z)
    r_yz2 = r_yz**2

    a = r_xy2 + r_yz2
    b = 2*r_xz*r_yz*r_xy
    c = a - b

    d = 1-r_xy2
    e = c/d
    ans = e**0.5
    #ans = (r_xz2+r_yz2-2*r_xz*r_yz*r_xy)/(1-r_xy2)**0.5 
    return ans 

stock_file_path = 'c:/Users/USER/Desktop/Data analyst shit/STOCK_DATA/AAPL.csv'
stock_file_path_2 = 'c:/Users/USER/Desktop/Data analyst shit/STOCK_DATA/MSFT.csv'
stock_file_path_3 = 'c:/Users/USER/Desktop/Data analyst shit/STOCK_DATA/^GSPC.csv'



historical_data = pd.read_csv(stock_file_path)
close_price = historical_data["Close"]
open_price = historical_data["Open"]

print(close_price.head().to_list()) #convert pandas dataframe to list



historical_data1 = pd.read_csv(stock_file_path_2)
close_price1 = historical_data1["Close"]
open_price1 = historical_data1["Open"]

print(close_price1.head().to_list())

historical_data2 = pd.read_csv(stock_file_path_3)
close_price2 = historical_data2["Close"]
open_price2 = historical_data2["Open"]

print(close_price2.head().to_list())

print("Meow")

appl_closing = close_price.to_list()
msft_closing = close_price1.to_list()
SnP_closing = close_price2.to_list()

appl_opening = open_price.to_list()
msft_opening = open_price1.to_list()
SnP_opening = open_price2.to_list()


def correlation_sum(open_1,open_2,close_1,close_2):
    print("Open Correlation", correlation(open_1,open_2))
    print("Close Correlation",correlation(close_1,close_2))

#Pair Correlation



#run the MULTI CORRELATIONNNNN

print(multi_correlation(appl_opening, msft_opening,SnP_opening))
print(multi_correlation(msft_opening, appl_opening,SnP_opening))
print(multi_correlation(SnP_opening, msft_opening,appl_opening))



#NEXT STEP DO A LOOP THROUGH ALL THE TICKERS AND FIND OUT THEIR CORRELATION
