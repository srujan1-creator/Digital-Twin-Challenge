"""
CardioTwin-India: FastAPI REST Microservice
Provides Digital Twin endpoints, model inference, 'what-if' simulation, and FHIR export.
"""

import os
import sys
import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from api.schemas import PatientEHR, WhatIfSimulationRequest, RiskPredictionResponse
from models.ehr_risk_predictor import CardioRiskPredictor
from models.physiological_sim import BergmanGlucoseInsulinModel, WindkesselHemodynamicModel
from models.glucose_forecast_lstm import WearableSequenceForecaster
from models.explainability import generate_clinical_explanation

app = FastAPI(
    title="CardioTwin-India API",
    description="Multimodal Digital Twin Engine for Cardio-Metabolic Disease & T2D in India",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data and models
data_dir = os.path.join(root_dir, "data")
ehr_path = os.path.join(data_dir, "patients_ehr.csv")
telemetry_path = os.path.join(data_dir, "wearables_cgm_telemetry.csv")
personas_path = os.path.join(data_dir, "sample_patient_profiles.json")

df_ehr = pd.read_csv(ehr_path) if os.path.exists(ehr_path) else None
df_telemetry = pd.read_csv(telemetry_path) if os.path.exists(telemetry_path) else None

with open(personas_path, "r", encoding="utf-8") as f:
    sample_personas = json.load(f)

predictor = CardioRiskPredictor()
predictor.load_models()
bergman = BergmanGlucoseInsulinModel()
forecaster = WearableSequenceForecaster()

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "CardioTwin-India Digital Twin Microservice",
        "models_loaded": predictor.ascvd_model is not None,
        "patients_count": len(df_ehr) if df_ehr is not None else 0
    }

@app.get("/api/patients")
def list_patients():
    return sample_personas

@app.get("/api/patient/{patient_id}")
def get_patient_profile(patient_id: str):
    # Check personas first
    for p in sample_personas:
        if p["patient_id"] == patient_id:
            return p
    # Fallback to EHR csv
    if df_ehr is not None:
        matched = df_ehr[df_ehr["patient_id"] == patient_id]
        if not matched.empty:
            return matched.iloc[0].to_dict()
    raise HTTPException(status_code=404, detail="Patient not found")

@app.post("/api/predict/risk")
def predict_risk(ehr: PatientEHR):
    pt_dict = ehr.model_dump()
    preds = predictor.predict_patient(pt_dict)
    
    windkessel = WindkesselHemodynamicModel(baseline_sbp=ehr.systolic_bp_mmhg, baseline_dbp=ehr.diastolic_bp_mmhg)
    hemo = windkessel.simulate_24h_cycle(nocturnal_dipping_impaired=True)
    
    explanation = generate_clinical_explanation(
        pt_dict,
        ascvd_risk=preds["ascvd_10yr_risk_pct"],
        dkd_stage=preds["dkd_stage_prediction"],
        dipping_status=hemo["dipper_status"]
    )
    
    return {
        "patient_id": ehr.patient_id,
        "predictions": preds,
        "hemodynamics": {
            "dipping_ratio_pct": round(hemo["dipping_ratio_pct"], 1),
            "dipper_status": hemo["dipper_status"],
            "mean_day_sbp": round(hemo["mean_day_sbp"], 1),
            "mean_night_sbp": round(hemo["mean_night_sbp"], 1)
        },
        "explainability": explanation
    }

@app.post("/api/simulate/what-if")
def simulate_what_if(req: WhatIfSimulationRequest):
    # Baseline vs Intervention simulation
    # Baseline scenario (standard meal, no exercise, current meds)
    baseline_sim = bergman.simulate(
        initial_glucose=145.0,
        meal_carbs_g=80.0,
        carb_absorption_rate=1.0,
        exercise_active=False,
        med_metformin=True,
        med_sglt2i=False,
        minutes=req.simulation_horizon_hours * 60
    )
    
    # Counterfactual Intervention scenario
    adjusted_carbs = 80.0 * (1.0 - (req.carb_intake_reduction_pct / 100.0))
    intervention_sim = bergman.simulate(
        initial_glucose=145.0,
        meal_carbs_g=adjusted_carbs,
        carb_absorption_rate=0.8 if req.carb_intake_reduction_pct > 20 else 1.0, # Lower GI fiber effect
        exercise_active=req.postprandial_exercise_mins >= 15,
        med_metformin=True,
        med_sglt2i=req.titrate_sglt2i,
        minutes=req.simulation_horizon_hours * 60
    )
    
    # Hemodynamic intervention
    windkessel = WindkesselHemodynamicModel(baseline_sbp=146.0, baseline_dbp=92.0)
    baseline_bp = windkessel.simulate_24h_cycle(nocturnal_dipping_impaired=True, arb_titrated=False)
    counterfactual_bp = windkessel.simulate_24h_cycle(
        nocturnal_dipping_impaired=False if req.titrate_telmisartan else True,
        arb_titrated=req.titrate_telmisartan,
        aerobic_activity_hrs=req.postprandial_exercise_mins / 60.0
    )
    
    return {
        "patient_id": req.patient_id,
        "glucose": {
            "baseline": {
                "peak_glucose": baseline_sim["peak_glucose"],
                "time_to_peak_min": baseline_sim["time_to_peak_min"],
                "time_in_range_pct": baseline_sim["time_in_range_pct"],
                "curve": baseline_sim["glucose_mgdl"].tolist()
            },
            "intervention": {
                "peak_glucose": intervention_sim["peak_glucose"],
                "time_to_peak_min": intervention_sim["time_to_peak_min"],
                "time_in_range_pct": intervention_sim["time_in_range_pct"],
                "curve": intervention_sim["glucose_mgdl"].tolist(),
                "peak_glucose_reduction": round(baseline_sim["peak_glucose"] - intervention_sim["peak_glucose"], 1),
                "tir_improvement_pct": round(intervention_sim["time_in_range_pct"] - baseline_sim["time_in_range_pct"], 1)
            }
        },
        "blood_pressure": {
            "baseline": {
                "dipper_status": baseline_bp["dipper_status"],
                "mean_day_sbp": baseline_bp["mean_day_sbp"],
                "mean_night_sbp": baseline_bp["mean_night_sbp"]
            },
            "intervention": {
                "dipper_status": counterfactual_bp["dipper_status"],
                "mean_day_sbp": counterfactual_bp["mean_day_sbp"],
                "mean_night_sbp": counterfactual_bp["mean_night_sbp"],
                "sbp_drop_day": round(baseline_bp["mean_day_sbp"] - counterfactual_bp["mean_day_sbp"], 1),
                "sbp_drop_night": round(baseline_bp["mean_night_sbp"] - counterfactual_bp["mean_night_sbp"], 1)
            }
        }
    }

@app.get("/api/fhir/patient/{patient_id}")
def export_fhir(patient_id: str):
    """
    Exports Patient and Observations according to HL7 FHIR R4 standard.
    """
    matched_persona = None
    for p in sample_personas:
        if p["patient_id"] == patient_id:
            matched_persona = p
            break
            
    if not matched_persona:
        matched_persona = sample_personas[0]
        
    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": matched_persona["patient_id"],
                    "name": [{"text": matched_persona["name"]}],
                    "gender": matched_persona["gender"].lower(),
                    "address": [{"city": matched_persona["city"]}],
                    "extension": [
                        {
                            "url": "http://happiesthealth.org/fhir/StructureDefinition/digital-twin-phenotype",
                            "valueString": matched_persona["phenotype"]
                        }
                    ]
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "status": "final",
                    "code": {"coding": [{"system": "http://loinc.org", "code": "4548-4", "display": "HbA1c"}]},
                    "subject": {"reference": f"Patient/{matched_persona['patient_id']}"},
                    "valueQuantity": {"value": matched_persona["hba1c"], "unit": "%"}
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "status": "final",
                    "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic Blood Pressure"}]},
                    "subject": {"reference": f"Patient/{matched_persona['patient_id']}"},
                    "valueQuantity": {"value": int(matched_persona["bp"].split("/")[0]), "unit": "mmHg"}
                }
            },
            {
                "resource": {
                    "resourceType": "RiskAssessment",
                    "status": "final",
                    "subject": {"reference": f"Patient/{matched_persona['patient_id']}"},
                    "prediction": [
                        {
                            "outcome": {"text": "10-Year ASCVD Cardiovascular Risk"},
                            "probabilityDecimal": matched_persona["ascvd_10yr"] / 100.0,
                            "qualitativeRisk": {"text": "High Risk (>20%)"}
                        }
                    ]
                }
            }
        ]
    }
    return fhir_bundle
