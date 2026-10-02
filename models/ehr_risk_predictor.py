"""
CardioTwin-India: Machine Learning EHR Multi-Target Risk Predictor
Trained on South Asian clinical cohort for:
1. 10-Year ASCVD Cardiovascular Risk Score
2. Diabetic Kidney Disease (DKD) progression stage
3. 90-Day Glycemic Decompensation Probability
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
import xgboost as xgb

FEATURE_COLS = [
    "age", "bmi", "waist_cm", "diabetes_duration_yr", "family_history_cad",
    "hba1c_pct", "fasting_glucose_mgdl", "postprandial_glucose_mgdl",
    "triglycerides_mgdl", "hdl_mgdl", "ldl_mgdl", "total_cholesterol_mgdl",
    "serum_creatinine_mgdl", "egfr_ml_min", "uacr_mg_g",
    "systolic_bp_mmhg", "diastolic_bp_mmhg", "resting_hr_bpm",
    "med_metformin", "med_sglt2i", "med_glimepiride", "med_statin", "med_telmisartan"
]

class CardioRiskPredictor:
    def __init__(self, models_dir=None):
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.ascvd_model = None
        self.dkd_model = None
        self.glycemic_model = None
        self.feature_cols = FEATURE_COLS

    def train_and_save(self, df_ehr):
        X = df_ehr[self.feature_cols]
        y_ascvd = df_ehr["ascvd_10yr_risk_pct"]
        y_dkd = df_ehr["dkd_stage"]
        y_glyc = df_ehr["glycemic_decompensation_risk"]
        
        # Train ASCVD Regressor using XGBoost
        self.ascvd_model = xgb.XGBRegressor(
            n_estimators=120,
            max_depth=4,
            learning_rate=0.08,
            random_state=42
        )
        self.ascvd_model.fit(X, y_ascvd)
        
        # Train DKD Classifier using Random Forest
        self.dkd_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.dkd_model.fit(X, y_dkd)
        
        # Train Glycemic Decompensation Regressor using XGBoost
        self.glycemic_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            random_state=42
        )
        self.glycemic_model.fit(X, y_glyc)
        
        # Persist models
        joblib.dump(self.ascvd_model, os.path.join(self.models_dir, "ascvd_xgb.joblib"))
        joblib.dump(self.dkd_model, os.path.join(self.models_dir, "dkd_rf.joblib"))
        joblib.dump(self.glycemic_model, os.path.join(self.models_dir, "glycemic_xgb.joblib"))
        print("Trained and persisted all 3 clinical risk models successfully.")

    def load_models(self):
        ascvd_path = os.path.join(self.models_dir, "ascvd_xgb.joblib")
        dkd_path = os.path.join(self.models_dir, "dkd_rf.joblib")
        glycemic_path = os.path.join(self.models_dir, "glycemic_xgb.joblib")
        
        if os.path.exists(ascvd_path) and os.path.exists(dkd_path) and os.path.exists(glycemic_path):
            self.ascvd_model = joblib.load(ascvd_path)
            self.dkd_model = joblib.load(dkd_path)
            self.glycemic_model = joblib.load(glycemic_path)
            return True
        return False

    def predict_patient(self, patient_dict):
        """
        Receives dictionary of patient EHR fields, returns multi-organ predictions.
        """
        if self.ascvd_model is None:
            success = self.load_models()
            if not success:
                raise RuntimeError("Models not loaded or trained yet.")
                
        # Fill missing features with default medians if needed
        features = []
        for col in self.feature_cols:
            features.append(patient_dict.get(col, 0.0))
            
        X_pt = pd.DataFrame([features], columns=self.feature_cols)
        
        pred_ascvd = float(self.ascvd_model.predict(X_pt)[0])
        pred_dkd = str(self.dkd_model.predict(X_pt)[0])
        pred_dkd_probs = {cls: float(prob) for cls, prob in zip(self.dkd_model.classes_, self.dkd_model.predict_proba(X_pt)[0])}
        pred_glyc = float(self.glycemic_model.predict(X_pt)[0])
        
        # Feature importances for explainability
        feature_importance_ascvd = dict(zip(self.feature_cols, self.ascvd_model.feature_importances_))
        sorted_importance = sorted(feature_importance_ascvd.items(), key=lambda x: x[1], reverse=True)[:6]
        
        return {
            "ascvd_10yr_risk_pct": round(pred_ascvd, 2),
            "ascvd_category": "High Risk (>20%)" if pred_ascvd >= 20.0 else ("Borderline Risk (10-20%)" if pred_ascvd >= 10.0 else "Low Risk (<10%)"),
            "dkd_stage_prediction": pred_dkd,
            "dkd_stage_probabilities": pred_dkd_probs,
            "glycemic_decompensation_probability": round(pred_glyc, 3),
            "top_risk_drivers": sorted_importance
        }
