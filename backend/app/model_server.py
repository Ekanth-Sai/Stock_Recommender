import joblib
import numpy as np
import pandas as pd
from typing import Tuple 

MODEL_PATH = "model.joblib"

class Recommender:
    def __init__(self, model_path = MODEL_PATH):
        self.model = joblib.load(model_path)

    def predict_prob(self, X : pd.DataFrame):
        probs = self.model.predict_proba(X)
        return probs 
    
    def predict_class(self, X : pd.DataFrame, thresh_buy = 0.6, thresh_sell = 0.6) -> Tuple[str, float]:
        probs = self.predict_proba(X)
        classes = self.model.classes_
        p = probs[-1]
        idx = p.argmax()
        cls = classes[idx]
        conf = p[idx]

        if cls == "buy" and conf >= thresh_buy:
            return "buy", float(conf)
        if cls == "sell" and conf >= thresh_sell:
            return "sell", float(conf)
        return "hold", float(conf)
    