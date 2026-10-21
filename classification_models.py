from sklearn.model_selection import cross_validate, TimeSeriesSplit # FIX: TimeSeriesSplit replaces random K-fold
from sklearn.dummy import DummyClassifier # FIX: baseline to compare the models against
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
# FIX: removed unused imports (numpy, accuracy_score, confusion_matrix, csv, weight_calculator) and ast (cleaning_data.py now casts to float)
# FIX: removed itertools.combinations, replaced by feature_groups below
from create_db import headers, limit # FIX: limit is needed to build the feature groups; module renamed from creating_SQL_DB_angrily
import sqlite3

# FIX: removed data_types, it only fed weight_calculator whose result (weight_set) was never used

models = {
    "Logistics Regression": LogisticRegression(),
    "Random Forest Classifier": RandomForestClassifier(),
    "SVC": SVC(),
    "K Neighbors Classifier": KNeighborsClassifier(),
    "Dummy (most frequent)": DummyClassifier(strategy="most_frequent"), # FIX: always guesses the majority class, a model has to beat this to be useful
}

#connect to SQLite DB
conn = sqlite3.connect("data_1m.db")

#Read data from a table into a DataFrame
df = pd.read_sql_query("SELECT * FROM my_table_cleaned", conn)

#
conn.close()
df = df.drop_duplicates()
df = df.sort_values('Open Time0').reset_index(drop = True) # FIX: rows are mined at random dates, sort by time so the CV folds train on the past and test on the future

#retrieve x-axis



features = headers.copy() # FIX: was features = headers, same list object, so .remove('y') also removed 'y' from headers
features.remove('y')
features = [x for x in features if not x.startswith('Open Time') and not x.startswith('Close Time')] # FIX: timestamps are not market information, drop them from the features

# FIX: removed the ast.literal_eval loop, cells are single numbers stored as TEXT (not lists like the old csv), cleaning_data.py casts them to float
# FIX: removed weight_set = weight_calculator(data_types,features), never used below


y = (df['y'] >df['last_close']).astype(int) #converting y into boolean


print(y)
print(y.value_counts(normalize = True)) # FIX: class balance, tells you what accuracy the Dummy baseline gets for free


siu = [0,0,0]
lowest = [0.5,0,0]
results = {}

#walk forward folds: each fold trains on earlier rows and tests on the rows after them
cv = TimeSeriesSplit(n_splits = 5) # FIX: cv=5 (StratifiedKFold) split rows in random-date order, so models trained on the future and tested on the past

#hand-picked feature groups # FIX: replaces every combination of features (~2^220 subsets, can never finish)
close_lags = ["Close" + str(c) for c in range(limit)] #"Close" + number so Close Time is not picked up
feature_groups = {
    "All features": features,
    "Close lags": close_lags,
    "Close + Volume lags": close_lags + ["Volume" + str(c) for c in range(limit)],
    "Taker Buy lags": ["Taker Buy Base" + str(c) for c in range(limit)] + ["Taker Buy Quote" + str(c) for c in range(limit)],
}

#evaluate?
for group, combo in feature_groups.items(): # FIX: was for r in range(2, len(features)+1): for combo in combinations(features,r)
    x_subset = df[combo]
    for name, model in models.items(): # FIX: this loop sat outside the combinations loop, so only the last combo of each size was scored

        scores = cross_validate(model, x_subset, y, cv=cv, scoring='accuracy') #since y is a boolean we dont use r2 for scoring # FIX: cv=5 -> TimeSeriesSplit
        results[(name, group)] = scores['test_score'].mean() # FIX: was results[name], overwritten by every feature group

        if scores['test_score'].mean() > siu[0]: #loop to return the highest accuracy guy
            siu[0] = scores['test_score'].mean()
            siu[1] = x_subset.columns
            siu[2] = name
        print(f"{name} Accuracy: {scores['test_score'].mean():.4f}", group) # FIX: re-enabled; scores is a dict so scores.mean() would crash
        if scores['test_score'].mean() < lowest[0]:
            lowest[0] = scores['test_score'].mean() # FIX: typo, 'test_scores' is not a key (KeyError whenever a model scored below 0.5)
            lowest[1] = x_subset.columns
            lowest[2] = name
print(siu[0], siu[1],siu[2])
print(lowest[0],lowest[1],lowest[2])

"""
for name, model in models.items():
    scores = cross_val_score(model,x2 , y, cv=5, scoring='accuracy')
    print(scores.mean())
"""

