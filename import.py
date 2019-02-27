import os
import re
import pandas as pd
import sqlite3

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()

sql = ''' INSERT INTO allocation_asset(codec, name) VALUES(?,?)'''

df = pd.read_csv("lista.csv", delimiter=";")

for index, row in df.iterrows():
    objectiveAllocation_asset = (row["codice"], row["asset"])
    cur.execute(sql, objectiveAllocation_asset)

conn.commit()

ql = ''' INSERT INTO allocation_series(asset_id, date, price) VALUES(?,?,?)'''

path = "data/"
for fname in os.listdir(path):
    if re.search(r'\.csv$', fname):
        name = fname.split("_")[0].replace(".csv", " ")
        df = pd.read_csv(path+"/"+fname)
        df.columns = ["date","price"]
        df["price"] = df["price"].apply(lambda x : round(x,3))
        for index, row in df.iterrows():
            objectiveAllocation_series = (name, row["date"], row["price"])
            cur.execute(sql, objectiveAllocation_series)
conn.commit()
conn.close()
