
import random
import time
import sqlite3 # FIX: needed to catch sqlite3.ProgrammingError below
import requests # FIX: needed to catch requests.exceptions.RequestException below
from functions import data_extraction_past_v3
from creating_SQL_DB_angrily import headers
#Generational talent for generating relevant headers


limit = 20
#random time generator
def zero_infront(value):
    if value < 10:
        value = "0" + str(value)
    else:
        value = str(value)
    return value

i = 1
while i != 0:
    year = random.randint(2018,2025) # FIX: BTCUSDT spot only starts 17 Aug 2017; earlier dates all returned that same first window, giving duplicate rows
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


    #as some dates do not have data, this could break the loop due to an error.
    try: 
        data_extraction_past_v3("BTCUSDT","1m",end_time,limit,headers) # FIX: v3 no longer takes the 5m interval/start time
        i += 1 
        if i == 100:
            i = 1
            time.sleep(20)
    except (ZeroDivisionError, IndexError) :
        continue
    except (requests.exceptions.RequestException, sqlite3.ProgrammingError) as e: # FIX: network/HTTP errors (incl. rate limits) and windows with fewer than 20 candles used to crash the miner
        print("skipped:", e)
        time.sleep(30) #back off so a rate limit does not turn into an IP ban
        continue

