"""
CardioTwin-India: Unit & Physiological Sanity Tests
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add root directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.physiological_sim import BergmanGlucoseInsulinModel, WindkesselHemodynamicModel
from models.glucose_forecast_lstm import WearableSequenceForecaster
from models.ehr_risk_predictor import CardioRiskPredictor

class TestCardioTwinModels(unittest.TestCase):
    def setUp(self):
        self.bergman = BergmanGlucoseInsulinModel()
        self.windkessel = WindkesselHemodynamicModel(baseline_sbp=140, baseline_dbp=88)
        self.forecaster = WearableSequenceForecaster()
        self.predictor = CardioRiskPredictor()
        self.predictor.load_models()

    def test_bergman_simulation(self):
        result = self.bergman.simulate(
            initial_glucose=140.0,
            meal_carbs_g=75.0,
            carb_absorption_rate=1.0,
            exercise_active=False,
            med_metformin=True,
            med_sglt2i=False,
            minutes=180
        )
        self.assertIn("glucose_mgdl", result)
        self.assertEqual(len(result["glucose_mgdl"]), 180)
        self.assertGreater(result["peak_glucose"], 140.0)
        self.assertTrue(50.0 <= result["peak_glucose"] <= 450.0)

    def test_counterfactual_exercise_reduces_glucose(self):
        res_sedentary = self.bergman.simulate(meal_carbs_g=75.0, exercise_active=False)
        res_exercise = self.bergman.simulate(meal_carbs_g=75.0, exercise_active=True)
        # Exercise should blunt peak glucose
        self.assertLess(res_exercise["peak_glucose"], res_sedentary["peak_glucose"])

    def test_windkessel_hemodynamics(self):
        bp_res = self.windkessel.simulate_24h_cycle(nocturnal_dipping_impaired=True)
        self.assertEqual(len(bp_res["systolic_bp"]), 288)
        self.assertIn("dipper_status", bp_res)
        self.assertGreater(bp_res["mean_day_sbp"], 90.0)

    def test_forecaster_trajectory(self):
        cgm = np.linspace(130, 160, 24)
        hr = np.linspace(72, 85, 24)
        fc = self.forecaster.forecast_trajectory(cgm, hr, meal_recent_carbs=50)
        self.assertEqual(len(fc["forecast_glucose"]), 24)
        self.assertEqual(len(fc["ci_upper_95"]), 24)
        self.assertGreater(fc["ci_upper_95"][0], fc["ci_lower_95"][0])

    def test_ehr_risk_prediction(self):
        sample_patient = {
            "age": 55, "bmi": 28.0, "waist_cm": 96.0, "diabetes_duration_yr": 8.0,
            "family_history_cad": 1, "hba1c_pct": 8.5, "fasting_glucose_mgdl": 165.0,
            "postprandial_glucose_mgdl": 240.0, "triglycerides_mgdl": 220.0,
            "hdl_mgdl": 38.0, "ldl_mgdl": 135.0, "total_cholesterol_mgdl": 217.0,
            "serum_creatinine_mgdl": 1.1, "egfr_ml_min": 75.0, "uacr_mg_g": 65.0,
            "systolic_bp_mmhg": 145, "diastolic_bp_mmhg": 92, "resting_hr_bpm": 78,
            "med_metformin": 1, "med_sglt2i": 0, "med_glimepiride": 1, "med_statin": 1, "med_telmisartan": 1
        }
        res = self.predictor.predict_patient(sample_patient)
        self.assertIn("ascvd_10yr_risk_pct", res)
        self.assertIn("dkd_stage_prediction", res)
        self.assertIn("glycemic_decompensation_probability", res)
        self.assertTrue(0.0 <= res["ascvd_10yr_risk_pct"] <= 100.0)

if __name__ == "__main__":
    unittest.main()
