# Perp-Future-Data

## Goal
Can the last 20 minutes of Bitcoin trading data predict which way the price moves next? This project samples random hours of BTCUSDT 1-minute candles from Binance (2018–2025), turns each one into a row of 20 lagged candle features, and labels it with whether the average close over the *next* 3 minutes ends up above the last close. It then compares a few standard scikit-learn classifiers against a baseline that always guesses the most common answer, using time-ordered cross-validation so no model is ever tested on data from before its training data.

## Pipeline
Run these from the repo folder, in this order:

1. `pip install -r requirements.txt`
2. `python create_db.py`: creates `data_1m.db` with the empty table `my_table` (222 columns).
3. `python data_miner.py`: loops until you stop it with Ctrl+C. Each loop:
   - picks a random UTC hour between 2018 and 2025;
   - fetches the 20 one-minute candles starting there, plus the next 3 to build the label;
   - appends one row to `my_table`.

   It pauses for 20 s every 99 samples, and for 30 s after any API error.
4. `python cleaning_data.py`: converts every column to a number, drops duplicate rows and rows with missing values, and writes `my_table_cleaned`.
5. `python classification_models.py`: prints the class balance, then the accuracy of each model on each feature group, then the best and worst results.

Other files:
- `DB_CHECK.PY` prints 5 random rows from `my_table`.
- `create_csv.py` and `data_extraction_past_v2` are the older CSV version of the pipeline.
- `OG_Code/` holds the first prototypes.

## Features and label
- **Data:** Binance **spot** BTCUSDT 1-minute candles from the public `/api/v3/klines` endpoint. Despite the repo name, this is *not* perpetual futures data: there's no funding rate, open interest or mark price.
- **Features:** the 11 fields of each candle × 20 lags. The fields are Open Time, Open, High, Low, Close, Volume, Close Time, Quote Asset Volume, Trades, Taker Buy Base and Taker Buy Quote. That gives 220 columns plus `last_close`. The Open Time and Close Time columns are dropped before modelling, which leaves **181 features**.
- **Feature groups compared:**
  - All features
  - Close lags (20)
  - Close + Volume lags (40)
  - Taker Buy Base + Quote lags (40)
- **Label:** `y = 1` if the mean close of the next three 1-minute candles is above `last_close` (the close of the 20th candle), otherwise `0`. The label window starts at the next candle's open, so it never includes a candle the features already saw.

## Validation method
- Each row is an independent sample from a random hour. The rows are sorted by `Open Time0`, then split with `TimeSeriesSplit(n_splits=5)`: every fold trains on earlier samples and tests on the block of samples that comes after them in time.
- The score is accuracy averaged over the 5 test folds.
- `DummyClassifier(strategy="most_frequent")` is the baseline. A model is only useful if it beats it.
- Models: Logistic Regression, Random Forest, SVC and K-Nearest Neighbours, all with scikit-learn's default settings.

## Results
One run on 21 Oct 2026: 1,000 samples mined, 989 left after removing 11 duplicates (the same random hour drawn twice). The samples run from 2018 to 2025. Class balance: 52.2% down/flat (`y = 0`), 47.8% up (`y = 1`). Accuracy is the mean over 5 `TimeSeriesSplit` test folds, 820 test rows in total.

| Model | All features (181) | Close lags (20) | Close + Volume lags (40) | Taker Buy lags (40) |
|---|---|---|---|---|
| Logistic Regression | 0.485 | 0.526 | 0.507 | 0.483 |
| Random Forest | 0.480 | 0.512 | 0.488 | 0.465 |
| SVC | 0.487 | 0.528 | 0.530 | 0.488 |
| K-Nearest Neighbours | 0.490 | 0.534 | **0.537** | 0.501 |
| **Baseline** (most frequent class) | 0.483 | 0.483 | 0.483 | 0.483 |

**How to read this:**
- **Why the baseline is below 50%:** "down/flat" is the majority class in the training folds, but the test folds contain slightly more "up" samples than that.
- **The best score isn't strong evidence:** KNN on Close + Volume lags scored 53.7%. That's about 5 percentage points above the baseline but under 4 above a coin flip. With 820 test rows, one standard error is about 1.7 points, and it's the best of 16 model/feature combinations, so some of that edge is likely luck.
- **Using all 181 features was no better than the baseline.**

This isn't evidence that the model predicts the next 3 minutes. A larger sample and stationary features (see below) would be the next steps.

## Limitations
- **Non-stationary features:** the features are raw price and volume levels. In this sample `last_close` ranges from about $3,200 to $125,300, so each time-ordered fold sees a price range the model never trained on. Returns or normalised features would suit these models better.
- **No feature scaling:** Logistic Regression, SVC and KNN are sensitive to feature scale. Logistic Regression also gives convergence warnings on the raw features.
- **Small sample:** 989 samples, so each test fold has 164 rows and one standard error of accuracy is about 1.7 percentage points. A difference of a few points between models is within noise.
- **No transaction costs:** accuracy isn't profit. Fees, the bid/ask spread and slippage aren't modelled. The median move behind a label is 0.04%, and 80% of the moves are smaller than Binance's 0.1% taker fee, so even a correct prediction would usually lose money after fees.
- **Not reproducible bit-for-bit:** `data_miner.py` doesn't set a random seed, so every run samples different hours.
- **Gaps in Binance's data:** if Binance has no candles for part of a window (for example during maintenance), the 20 candles can span the gap and not be consecutive minutes.
