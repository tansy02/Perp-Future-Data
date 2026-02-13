import csv 
import sqlite3

limit = 20
data_types= ["Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Trades",
        "Taker Buy Base", "Taker Buy Quote"]
headers = []
for i in range(len(data_types)):
    

    for c in range(limit):
        a = str(c)
        abc = data_types[i] + a
        headers.append(abc)
headers.append('y')
headers.append('last_close')

#writer headers to csv
with open('data_5m.csv',mode='w', newline = '') as file:
    writer = csv.writer(file)
    writer.writerow(headers)

#connect to (or create a database)
conn = sqlite3.connect("data_5m.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    name TEXT,
    age INTEGER,
    score REAL
)
""")