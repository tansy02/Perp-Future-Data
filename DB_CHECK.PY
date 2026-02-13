import sqlite3

conn = sqlite3.connect('data_1m.db')
cursor = conn.cursor()

# Insert data (example)

# Check if data is appended
cursor.execute("SELECT * FROM my_table ORDER BY RANDOM() LIMIT 5") #check random data
rows = cursor.fetchall()

if rows:
    print("Data appended successfully:")
    for row in rows:
        print(row)
else:
    print("No matching data found.")

cursor.close()
conn.close()