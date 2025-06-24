import sqlite3
import pandas as pd

# Step 1: Connect and read the data
conn = sqlite3.connect("data_5m.db")
df = pd.read_sql_query("SELECT * FROM my_table", conn)

df = df.apply(pd.to_numeric, errors='coerce') #convert entire df into numeric aka floats

#Optional: If your data shit can use this to handle missing values
#df = df.apply(pd.dropna)

df.to_sql("my_table_cleaned", conn, if_exists = 'replace', index= False)

conn.close()