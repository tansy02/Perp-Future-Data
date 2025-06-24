from data_functions import data_extraction_present
from data_functions import data_extraction_past
import random
import time
from The_new_guy import data_extraction_past_v3
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


    #as some dates do not have data, this could break the loop due to an error.
    try: 
        data_extraction_past_v3("BTCUSDT","1m","5m",end_time,end_time,limit,headers)
        i += 1 
        if i == 100:
            i = 1
            time.sleep(20)
    except (ZeroDivisionError, IndexError) :
        continue

