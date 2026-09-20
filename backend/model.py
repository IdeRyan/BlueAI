import joblib
import pandas as pd

random_forest_model = joblib.load("./models/blue_ai_model.pkl")

FEATURE_NAMES = ["flow1_avg", "flow2_avg", "flow_diff", "flow_ratio", "flow2_var"]

def predict(features: list):
    features_df = pd.DataFrame([features], columns=FEATURE_NAMES)
    label = random_forest_model.predict(features_df)[0]
    confidence = max(random_forest_model.predict_proba(features_df)[0])
    return int(label), float(confidence)