import pandas as pd 
import numpy as np
from sklearn.ensemble import RandomForestClassifier 
from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.metrics import classification_report
import joblib 
from data_fetcher import fetch_historical_data
from features import add_techincal_indicators   

def build_labels(df: pd.DataFrame, forward_window = 1, thresh = 0.005):
    df = df.copy()
    df['Future_Close'] = df['close'].shift(-forward_window)
    df['Future_Return'] = (df['Future_Close'] - df['close']) / df['close']

    def label_func(r):
        if pd.isna(r):
            return np.nan
        if r > thresh:
            return 'buy'
        elif r < -thresh:
            return 'sell'
        else:
            return 'hold'
    
    df['label'] = df['Future_Return'].apply(label_func)
    return df

def train(ticker = "INFY.NS", save_path = "model.joblib"):
    raw = fetch_historical_data(ticker, period = "5y", interval = "1d")
    df = add_techincal_indicators(raw)
    df = build_labels(df, forward_window = 1, thresh = 0.007)   

    df = df.dropna(subset = ['rsi_14', 'sma_20', 'sma_50', 'macd', 'atr_14', 'label'])
    features = ['rsi_14', 'sma_20', 'sma_50', 'macd', 'macd_signal', 'atr_14', 'volume', 'Return_1d']
    X = df[features]
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42, shuffle = False)
    
    tscv = TimeSeriesSplit(n_splits=5)
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        params = {'n_estimators': [100, 200, 300], 'max_depth': [5, 10, 20]}
        grid = GridSearchCV(RandomForestClassifier(class_weight='balanced'), params, cv=3)
        grid.fit(X_train, y_train)
        clf = grid.best_estimator_
        
        preds = clf.predict(X_test)
        print(classification_report(y_test, preds))

    joblib.dump(clf, save_path)
    print(f"Model saved to {save_path}")

if __name__ == "__main__":
    train()