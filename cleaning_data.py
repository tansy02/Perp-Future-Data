# FIX: new file, nothing created my_table_cleaned which both classifiers read
import sqlite3
import pandas as pd

#connect to SQLite DB
conn = sqlite3.connect("data_1m.db")

#read the raw table that data_miner appends to
df = pd.read_sql_query("SELECT * FROM my_table", conn)
print(len(df), "raw rows")

#every column was created as TEXT so sqlite stores the numbers as strings, convert entire df into numeric aka floats
df = df.apply(pd.to_numeric, errors='coerce') #anything that is not a number becomes NaN

#drop repeated samples and rows with missing values
df = df.drop_duplicates()
df = df.dropna()
print(len(df), "rows after cleaning")

#write it back as a new table, replace the old cleaned table if it exists
df.to_sql("my_table_cleaned", conn, if_exists = 'replace', index = False)

conn.close()
