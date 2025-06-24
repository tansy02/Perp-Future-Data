from sklearn.model_selection import cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import numpy as np
from itertools import combinations
from sklearn.metrics import accuracy_score, confusion_matrix
import ast
import csv
from The_new_guy import weight_calculator
from creating_SQL_DB_angrily import headers
import sqlite3

#weight calculating of the data
data_types = ['Open_Time','Open','High','Low','Close','Volume','Close_Time','Quote_Asset_Volume',
            'Trades','Taker_Buy_Base','Taker_Buy_Quote','last_close']

models = {
    "Logistics Regression": LogisticRegression(),
    "Random Forest Classifier": RandomForestClassifier(),
    "SVC": SVC(),
    "K Neighbors Classifier": KNeighborsClassifier(),
}

#connect to SQLite DB
conn = sqlite3.connect("data_1m.db")

#Read data from a table into a DataFrame
df = pd.read_sql_query("SELECT * FROM my_table_cleaned", conn)

#
conn.close()
df = df.drop_duplicates()

#retrieve x-axis



features = headers
features.remove('y')

for x in headers: #need to parse data from csv properly
    try:
        df[x] = df[x].apply(ast.literal_eval)
    except (ValueError):
        continue
weight_set = weight_calculator(data_types,features)


y = (df['y'] >df['last_close']).astype(int) #converting y into boolean


print(y)


siu = [0,0,0]
lowest = [0.5,0,0]
results = {}

#evaluate?
for r in range(2, len(features)+1):
    for combo in combinations(features,r):
        x_subset = df[list(combo)]
    for name, model in models.items():

        scores = cross_validate(model, x_subset, y, cv=5, scoring='accuracy') #since y is a boolean we dont use r2 for scoring
        results[name] = scores['test_score'].mean()

        if scores['test_score'].mean() > siu[0]: #loop to return the highest accuracy guy
            siu[0] = scores['test_score'].mean()
            siu[1] = x_subset.columns
            siu[2] = name
        #print(f"{name} Accuracy: {scores.mean():.4f}", x_subset.columns)
        if scores['test_score'].mean() < lowest[0]:
            lowest[0] = scores['test_scores'].mean()
            lowest[1] = x_subset.columns
            lowest[2] = name
print(siu[0], siu[1],siu[2])
print(lowest[0],lowest[1],lowest[2])

"""
for name, model in models.items():
    scores = cross_val_score(model,x2 , y, cv=5, scoring='accuracy')
    print(scores.mean())
"""

