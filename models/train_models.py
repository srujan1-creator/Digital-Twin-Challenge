"""
CardioTwin-India: Model Training Pipeline
Trains and serializes the multi-target predictive risk models.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from ehr_risk_predictor import CardioRiskPredictor

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ehr_csv = os.path.join(base_dir, "data", "patients_ehr.csv")
    
    if not os.path.exists(ehr_csv):
        raise FileNotFoundError(f"EHR dataset not found at {ehr_csv}. Run synthetic_generator.py first.")
        
    df_ehr = pd.read_csv(ehr_csv)
    print(f"Loaded EHR cohort with {len(df_ehr)} records.")
    
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")
    predictor = CardioRiskPredictor(models_dir=models_dir)
    predictor.train_and_save(df_ehr)
    
    # Test inference on first patient
    pt_sample = df_ehr.iloc[0].to_dict()
    result = predictor.predict_patient(pt_sample)
    print("\n--- Test Inference on Sample Patient ---")
    print(f"Patient ID: {pt_sample['patient_id']}")
    print(f"Predicted ASCVD 10-Yr Risk: {result['ascvd_10yr_risk_pct']}% ({result['ascvd_category']})")
    print(f"Predicted DKD Stage: {result['dkd_stage_prediction']}")
    print(f"Glycemic Decompensation Risk: {result['glycemic_decompensation_probability']}")
    print("Top Risk Drivers:")
    for feat, imp in result['top_risk_drivers']:
        print(f"  - {feat}: {imp:.4f}")

if __name__ == "__main__":
    main()
