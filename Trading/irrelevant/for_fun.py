import csv 
import pandas as pd
import ast
from data_functions import MA
import csv
import ast
import pandas as pd

file = r"C:\Leisure\Data analyst shit\Trading\data_5m.csv"
df = pd.read_csv(r"C:\Leisure\Data analyst shit\Trading\data_5m.csv")





#y = (df['y'] >df['last_close']).astype(int) #converting y into boolean
features = ['Open_Time','Open','High','Low','Close','Volume','Close_Time','Quote_Asset_Volume',
            'Trades','Taker_Buy_Base','Taker_Buy_Quote','y','last_close']
"""
for x in features:
    try:
        df[x] = df[x].apply(ast.literal_eval)
    except (ValueError):
        continue

print(df['Close'].describe())
#computing list by list aka row by row, use keyword 'apply' to iterate row by row
df['MA_5'] = df['Close'].apply(lambda x: MA(x,5)) #take each row as x and run it through the function MA(x)
print(df['MA_5'])

#print(df["y"])
#rint(df["last_close"])
"""

"""
file_path = r"C:\Leisure\Data Analyst shit\Trading\test.csv"

with open(file_path, mode='a', newline='') as file:
    writer = csv.writer(file)
        
    #append the data
    writer.writerow(y.values.tolist()) #dk why when you use print command to check its fucked up
"""
#print(MA(Close[0],5))

data_types = ["Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote",'y','last_close']

weight_ea = 1.0/len(data_types)

#receive headers of csv file; retrieving data headers

with open(r"C:\Leisure\Data Analyst shit\Trading\data_5m.csv", mode='r') as file:
    reader = csv.reader(file)
    headers = next(reader)
    
headers.append('Ignore') #added to fix the while loop 
c = 0  
weight = []
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

print(weight)
print(weight_ea)
print(sum(weight))

def weight_calculator(data_types, csv_file_path):
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
