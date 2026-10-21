# Changes

A list of the bugs fixed on `fix/pipeline`: what each one was, why it mattered, and where it was fixed. Each fix is one commit, and every changed line in the code is marked with a `# FIX:` comment. Line numbers refer to the files as they are after all the fixes.

---

## Fix 1: the 1m label was built from past 5m candles
- **Bug:** `data_extraction_past_v3` (and `_v2`) asked Binance for the next three 1-minute candles, but then built the label DataFrame from `data_5m`, which at that point held the 20 *historical* 5-minute candles.
- **Why it mattered:** `y` was the mean of past 5-minute closes, not the future price. The model was learning to predict something it had already been shown, so any accuracy it reported meant nothing.
- **Change:** build the DataFrame from `data_1m`, the future candles that were just fetched.
- **Where:** `functions.py:268` (v3), `functions.py:94` (v2).

## Fix 2: the label window included the current bar (leakage)
- **Bug:** the "future" request used `startTime = end_1m`, the Open Time of the last historical bar. Binance's `startTime` is inclusive, so the first of the "next 3" candles was the bar the features already ended on.
- **Why it mattered:** one of the three closes averaged into `y` was `last_close` itself, so the label leaked the current price and pulled `y` towards `last_close`.
- **Change:** start from the last bar's Close Time + 1 ms. Binance's Close Time is Open Time + 59,999 ms, so this is exactly the next bar's open. I checked a mined row against Binance: the first label bar opens 60 s after `Open Time19`.
- **Where:** `functions.py:251` (v3), `functions.py:49` and `:80` (v2).

## Fix 3: dates were converted in local time, not UTC
- **Bug:** `date_to_milliseconds` used `time.mktime`, which treats the date string as local time (UTC+8 in Singapore).
- **Why it mattered:** every request started 8 hours earlier than the date it printed, so the logs and the data didn't match. On a machine in another time zone you'd get different data from the same dates.
- **Change:** `calendar.timegm`, which treats the date as UTC, the time zone Binance's timestamps use.
- **Where:** `functions.py:5`, `functions.py:14`.

## Fix 4: importing functions.py ran code
- **Bug:** the random-date generator at module level in `functions.py` ran, and printed, every time `data_miner.py` or a classifier imported the module.
- **Why it mattered:** importing a module shouldn't do anything. It also cluttered the output and drew random numbers nobody used.
- **Change:** wrapped the block in `if __name__ == "__main__":`.
- **Where:** `functions.py:193`.

## Fix 5: unused imports
- **Bug:** `functions.py` imported `matplotlib`, `numpy`, three `hyperliquid` modules and `eth_account` without using any of them. The classifier imported `numpy`, `csv`, `accuracy_score`, `confusion_matrix` and `weight_calculator`, and computed a `weight_set` it never used.
- **Why it mattered:** you couldn't run the pipeline without installing packages it never uses, including a crypto wallet library. The unused imports also made it harder to see what the code actually depends on.
- **Change:** removed them, plus an unused global `dt` and the unused `weight_set`/`data_types`.
- **Where:** `functions.py:2`, `:11`; `classification_models.py:8`, `:13`, `:43`; `create_db.py:1`.

## Fix 6: nothing created `my_table_cleaned`
- **Bug:** both classifiers read `my_table_cleaned` from `data_1m.db`, but no script created it.
- **Why it mattered:** the modelling step couldn't run. Also, every column is created as `TEXT`, so SQLite stores each number as a string such as `'27123.45'`.
- **Change:** a new `cleaning_data.py` reads `my_table`, converts every column to a number (`pd.to_numeric`), drops duplicates and rows with missing values, and writes `my_table_cleaned`. The old `ast.literal_eval` loop in the classifier was left over from when CSV cells held whole lists. Now that each cell holds one number, it's just a slow float conversion, so I removed it.
- **Where:** `cleaning_data.py`; `classification_models.py:42`.

## Fix 7: the model search could never finish, and didn't score what it seemed to
- **Bugs:**
  - The `models` loop was indented outside the `combinations` loop, so only the last feature subset of each size was ever scored.
  - Trying every subset of about 220 features is about 2^220 fits, which can never finish.
  - `scores['test_scores']` was a typo, raising `KeyError` the first time a model scored below 0.5.
  - `features = headers` made both names point to the same list, so `.remove('y')` also removed `'y'` from `headers`. As a result the parsing loop never converted `y`, and `y > last_close` compared a string with a float and crashed.
  - The Open Time and Close Time columns were being used as features.
- **Why it mattered:** the script either crashed or ran forever. Even if it had finished, the results wouldn't have meant what they appeared to.
- **Change:** a small dict of hand-picked feature groups (all features, Close lags, Close + Volume lags, Taker Buy lags), with the models loop inside it and the same `siu`/`lowest` best/worst tracking. Also fixed the typo, used `headers.copy()`, and dropped the timestamp columns, leaving 181 features.
- **Where:** `classification_models.py:38`, `:40`, `:60`–`:83`.

## Fix 8: validation trained on the future
- **Bug:** samples are mined at random dates and stored in that random order. `cv=5` uses a `StratifiedKFold` with no shuffling, which splits the rows in the order they're stored, so models were trained on later dates and tested on earlier ones.
- **Why it mattered:** that's look-ahead bias, so the accuracy wasn't a fair estimate of predicting the future. There was also no baseline, so a score like 57% couldn't be judged: if 57% of labels are "up", always guessing "up" scores 57%.
- **Change:** sort by `Open Time0` and use `TimeSeriesSplit(n_splits=5)`, where each fold trains on the past and tests on the next block of time. Added `DummyClassifier(strategy="most_frequent")` as a baseline, and the script now prints the class balance of `y`.
- **Where:** `classification_models.py:1`–`2`, `:20`, `:32`, `:50`, `:58`, `:74`.

## Fix 9: the feature-weighting script could not work as designed
- **Bug:** `weight_calculator` returns one weight per *feature* (column), but `classification_weight.py` passed it as `sample_weight`, which sklearn expects to be one weight per *row*. The column matching also used `in` (a substring test) with underscore names (`Open_Time`) against space names (`Open Time0`). As a result:
  - `'Open'` also matched the `Open Time` columns.
  - The pointer stalled at `Close Time0`, so every later column got no weight.
  - It returned 120 weights for 221 features.

  On top of that, the script indexed a DataFrame with `[train_index]` (which needs `.iloc`) and indexed a list with `['test_score']`.
- **Why it mattered:** it crashed. Even with those bugs fixed, the idea was wrong: a per-feature weight isn't a per-row sample weight.
- **Change:** deleted `classification_weight.py`, plus `weight_calculator` and `weight_calculator_csv`, which nothing else used.
- **Where:** `classification_weight.py` (deleted); `functions.py:219`.

## Fix 10: dead code and hardcoded paths
- **Bug:** `creating_csv_angrily.py` still created a tutorial `students` table in `data_5m.db`. `data_extraction_past_v2` wrote CSVs to a hardcoded `C:\Leisure\...` path.
- **Why it mattered:** the dead code was confusing, and the hardcoded path only existed on one laptop. The path inside the commented-out string also triggered an invalid-escape `SyntaxWarning`.
- **Change:** removed the `students` table and its unused SQLite connection, and switched to relative paths (`data_1m.csv`, `data_5m.csv`).
- **Where:** `create_csv.py:2`, `:24`; `functions.py:139`, `:158`, `:170`, `:180`.

## Fix 11: years before BTCUSDT existed
- **Bug:** the random year was drawn from 2015–2025, but BTCUSDT spot trading on Binance starts on 17 Aug 2017.
- **Why it mattered:** `startTime` is a lower bound, so every date before the listing returned the *same* first candles (17 Aug 2017 04:00 UTC). About a quarter of all samples (2015, 2016 and January to mid-August 2017) were identical rows.
- **Change:** draw years from 2018–2025.
- **Where:** `data_miner.py:22`; `functions.py:194`.

## Fix 12: the 5m write crashed a fresh run
- **Bug:** `create_db.py` only creates `my_table` in `data_1m.db`, but `_v3` also inserted every sample into `my_table` in `data_5m.db`.
- **Why it mattered:** on a fresh run the first insert raised `sqlite3.OperationalError`, which the miner didn't catch, so mining stopped after one sample.
- **Change:** nothing downstream reads 5m data, so `_v3` no longer collects it. That removes two API calls per sample and the now-unused `interval_2`/`start_time2` parameters.
- **Where:** `functions.py:223`, `:257`, `:277`, `:305`; `data_miner.py:49`.

## Fix 13: rate limits and short windows
- **Bug:** when Binance rate-limits you (HTTP 429/418), the reply is a JSON error object. That became an empty DataFrame, then an `IndexError`, which the miner caught and retried *immediately*. Network errors, and windows with fewer than 20 candles (`sqlite3.ProgrammingError`, wrong number of values), weren't caught at all.
- **Why it mattered:** retrying instantly on a rate limit is how a temporary rate limit turns into an IP ban, and the uncaught errors stopped a long mining run.
- **Change:** `_v3` calls `resp.raise_for_status()` after each request. `data_miner.py` catches `RequestException` and `sqlite3.ProgrammingError`, prints the error and waits 30 s.
- **Where:** `functions.py:234`, `:265`; `data_miner.py:4`–`5`, `:56`.

---

## Repo hygiene
- Renamed `creating_SQL_DB_angrily.py` → `create_db.py` and `creating_csv_angrily.py` → `create_csv.py`, and updated the two imports (`data_miner.py:7`, `classification_models.py:10`).
- Added `requirements.txt` (only the packages the code imports) and `.gitignore` (local `*.db` and `*.csv` files, `__pycache__/`, scratch folder).
- Started tracking `OG_Code/` (the first prototypes), with their unused imports removed.
- Added `README.md`.
