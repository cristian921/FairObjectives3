import os
import re
import pandas as pd
import psycopg2

conn = psycopg2.connect("postgres://ckxgwxhfzizyde:3662b2977886196a29861917fad35c61e20c2673"
                        "74a48d172ea0fb98f528fb8c@ec2-174-129-224-157.compute-1.amazonaws.com:5432/dbh437o8dic5fm")

cur = conn.cursor()

sql = ''' INSERT INTO allocation_asset(codec, name) VALUES(%s,%s)'''

df = pd.read_csv("lista.csv", delimiter=";")

for index, row in df.iterrows():
    objectiveAllocation_asset = (row["codice"], row["asset"], )
    cur.execute(sql, objectiveAllocation_asset)

conn.commit()

sql = ''' INSERT INTO allocation_series(asset_id, date, price) VALUES(%s,%s,%s)'''

path = "data/"
for fname in os.listdir(path):
    if re.search(r'\.csv$', fname):
        name = fname.split("_")[0].replace(".csv", " ")
        df = pd.read_csv(path+"/"+fname)
        df.columns = ["date", "price"]
        df["price"] = df["price"].apply(lambda x: round(x, 3))
        print(name)
        for index, row in df.iterrows():
            objectiveAllocation_series = (name, row["date"], row["price"],)
            print(objectiveAllocation_series)
            cur.execute(sql, objectiveAllocation_series)
        conn.commit()
conn.close()
