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


#create the same table in both DBs (data_extraction_past_v3 writes to both)
for db_path in ["data_1m.db", "data_5m.db"]:
    #connect to (or create a database)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #create a table
    table_name = 'my_table'

    #generate SQL statement
    columns = ",".join([f'"{col}" TEXT' for col in headers])  #use TEXT as default type
    create_stmt = f'CREATE TABLE IF NOT EXISTS {table_name}({columns});'

    #EXECUTE IT
    cursor.execute(create_stmt)
    conn.commit()
    conn.close()
