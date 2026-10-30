from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from itertools import combinations
from functions import load_data, feature_types, family_columns

db_path = "data_1m.db" #or "data_5m.db"
limit = 20

#scaler inside the pipeline so it is fit on the training folds only (no leakage into the test fold)
#SVC and KNN are distance based, without scaling the biggest-number column dominates
models = {
    "Logistics Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter = 1000)),
    "Random Forest Classifier": RandomForestClassifier(random_state = 42),
    "SVC": make_pipeline(StandardScaler(), SVC()),
    "K Neighbors Classifier": make_pipeline(StandardScaler(), KNeighborsClassifier()),
}

X_all, y_all = load_data(db_path, limit)
print(len(y_all), "rows | share of up moves:", round(y_all.mean(), 4))

#hold out 20% that the subset search never sees. picking the best of ~2000 (model, subset) pairs
#by CV score will look good by luck alone, the held-out score is the honest number
X, X_holdout, y, y_holdout = train_test_split(X_all, y_all, test_size = 0.2, stratify = y_all, random_state = 42)

#StratifiedKFold keeps the up/down ratio the same in every fold
cv = StratifiedKFold(n_splits = 5, shuffle = True, random_state = 42)

#baseline: always guess the most common class. any model has to beat this to mean anything
baseline = cross_validate(DummyClassifier(strategy = "most_frequent"), X, y, cv = cv, scoring = 'accuracy')
baseline_acc = baseline['test_score'].mean()
print(f"Baseline (majority class) accuracy: {baseline_acc:.4f}")


results = {}

#feature subset testing over whole data types (eg all 20 'Close' columns together), not single columns.
#9 types -> 2^9 - 1 = 511 subsets. single columns would be ~2^180 subsets, which never finishes
for r in range(1, len(feature_types)+1):
    for combo in combinations(feature_types, r):
        cols = []
        for data_type in combo:
            cols += family_columns(data_type, limit)
        x_subset = X[cols]

        for name, model in models.items(): #inside the combo loop, so every subset gets tested
            scores = cross_validate(model, x_subset, y, cv = cv, scoring = 'accuracy', n_jobs = -1) #since y is a boolean we dont use r2 for scoring
            results[(name, combo)] = scores['test_score'].mean()


#rank every (model, subset) by accuracy
ranked = sorted(results.items(), key = lambda item: item[1], reverse = True)

print("\nTop 10:")
for (name, combo), acc in ranked[:10]:
    print(f"{acc:.4f} (+{acc - baseline_acc:.4f} vs baseline) | {name} | {', '.join(combo)}")

print("\nBottom 5:")
for (name, combo), acc in ranked[-5:]:
    print(f"{acc:.4f} | {name} | {', '.join(combo)}")

print("\nBest subset per model:")
for name in models:
    best = max((item for item in ranked if item[0][0] == name), key = lambda item: item[1])
    print(f"{best[1]:.4f} | {name} | {', '.join(best[0][1])}")


#final check: refit the overall best on all the search data, score once on the held-out 20%
(best_name, best_combo), best_cv = ranked[0]
cols = []
for data_type in best_combo:
    cols += family_columns(data_type, limit)

best_model = models[best_name]
best_model.fit(X[cols], y)
holdout_acc = accuracy_score(y_holdout, best_model.predict(X_holdout[cols]))
holdout_baseline = max(y_holdout.mean(), 1 - y_holdout.mean())

print(f"\nHeld-out: {best_name} | {', '.join(best_combo)}")
print(f"CV accuracy {best_cv:.4f} -> held-out accuracy {holdout_acc:.4f} (baseline {holdout_baseline:.4f})")
