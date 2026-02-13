from sklearn.model_selection import StratifiedKFold
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
from functions import weight_calculator
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

#initilize kf folds straitfiedKFold is used for classifications, otherwise use KFold for regression
cv = StratifiedKFold(n_splits = 5, shuffle= True, random_state = 42)


#evaluate?
for r in range(2, len(features)+1):
    for combo in combinations(features,r):
        x_subset = df[list(combo)]
        #have to redo the sample weight creator
    for name, model in models.items():
        scores = []
        #koop below is the error
        for train_index, test_index, in cv.split(x_subset,y):
            X_train, X_test = x_subset[train_index], x_subset[test_index]
            y_train, y_test = y[train_index], y[test_index]
            w_train = weight_set[train_index]

            try:
                model.fit(X_train,y_train, sample_weight = w_train)
            except TypeError: #for models like k neighbors which do not accept sample weights
                model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_pred,y_test)
            scores.append(acc)
            
        mean_score = np.mean(scores)
        results[(name,combo)] = mean_score
        

        if mean_score > siu[0]: #loop to return the highest accuracy guy
            siu[0] = scores['test_score'].mean()
            siu[1] = x_subset.columns
            siu[2] = name
        #print(f"{name} Accuracy: {scores.mean():.4f}", x_subset.columns)
        if mean_score < lowest[0]:
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

