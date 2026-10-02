"""
CardioTwin-India: API Schemas & FHIR Models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PatientEHR(BaseModel):
    patient_id: str
    age: int
    gender: str
    bmi: float
    waist_cm: float
    diabetes_duration_yr: float
    family_history_cad: int
    hba1c_pct: float
    fasting_glucose_mgdl: float
    postprandial_glucose_mgdl: float
    triglycerides_mgdl: float
    hdl_mgdl: float
    ldl_mgdl: float
    total_cholesterol_mgdl: float
    serum_creatinine_mgdl: float
    egfr_ml_min: float
    uacr_mg_g: float
    systolic_bp_mmhg: int
    diastolic_bp_mmhg: int
    resting_hr_bpm: int
    med_metformin: int = 1
    med_sglt2i: int = 0
    med_glimepiride: int = 0
    med_statin: int = 1
    med_telmisartan: int = 1

class WearableDataPoint(BaseModel):
    timestamp: str
    cgm_glucose_mgdl: float
    heart_rate_bpm: float
    hrv_rmssd_ms: float
    systolic_bp_mmhg: float
    diastolic_bp_mmhg: float
    step_count: int

class WhatIfSimulationRequest(BaseModel):
    patient_id: str
    carb_intake_reduction_pct: float = Field(default=0.0, description="0 to 50% carb reduction")
    postprandial_exercise_mins: int = Field(default=0, description="0 to 45 mins walking")
    titrate_sglt2i: bool = Field(default=False, description="Add or titrate SGLT2 inhibitor")
    titrate_telmisartan: bool = Field(default=False, description="Add or titrate ARB for blood pressure")
    simulation_horizon_hours: int = Field(default=4, description="Hours to project forward")

class RiskPredictionResponse(BaseModel):
    patient_id: str
    ascvd_10yr_risk_pct: float
    ascvd_category: str
    dkd_stage_prediction: str
    glycemic_decompensation_probability: float
    top_risk_drivers: List[tuple]
    clinical_action_plan: List[str]
