"""
CardioTwin-India: Synthetic Clinical & Wearable Dataset Generator
Calibrated against ICMR-INDIAB (Indian Council of Medical Research - India Diabetes) studies
and ADA/ACC cardiovascular risk guidelines for South Asian populations.
"""

import json
import os
import numpy as np
import pandas as pd

def generate_cohort(n_patients=500, random_seed=42):
    np.random.seed(random_seed)
    
    patient_ids = [f"IND-PT-{1000 + i}" for i in range(n_patients)]
    
    # Demographics & Lifestyle
    ages = np.random.normal(52, 11, n_patients).clip(25, 82).astype(int)
    genders = np.random.choice(["Male", "Female"], n_patients, p=[0.54, 0.46])
    locations = np.random.choice(["Bengaluru", "Mumbai", "Delhi-NCR", "Chennai", "Hyderabad", "Kolkata", "Pune"], n_patients)
    diet_types = np.random.choice(["Vegetarian (High Carb)", "Non-Vegetarian (Mixed)", "Ovo-Lacto Vegetarian"], n_patients, p=[0.55, 0.35, 0.10])
    
    # Asian Indian Phenotype: normal/lower BMI cutoffs for overweight (>=23) and obesity (>=25)
    # Higher visceral adiposity / waist-to-hip ratio
    bmis = np.random.normal(26.4, 4.2, n_patients).clip(18.5, 41.0).round(1)
    waist_circumference = (bmis * 3.2 + np.where(genders == "Male", 8.0, 5.0) + np.random.normal(0, 4.0, n_patients)).clip(65, 125).round(1)
    
    # Diabetes & Metabolic History
    diabetes_durations = np.random.exponential(6.0, n_patients).clip(0.5, 30.0).round(1)
    family_history_cad = np.random.choice([0, 1], n_patients, p=[0.42, 0.58])
    smoker_status = np.random.choice(["Never", "Former", "Current"], n_patients, p=[0.68, 0.18, 0.14])
    
    # Clinical Lab Biomarkers
    # HbA1c distribution with typical Indian outpatient spread (6.2% to 11.5%)
    hba1c = np.random.normal(7.8, 1.4, n_patients).clip(5.7, 13.0).round(2)
    fasting_glucose = (hba1c * 19.5 + np.random.normal(0, 18, n_patients)).clip(85, 330).round(1)
    postprandial_glucose = (fasting_glucose * 1.45 + np.random.normal(15, 25, n_patients)).clip(110, 450).round(1)
    
    # Lipid Profile (Atherogenic dyslipidemia typical in Indians: High Triglycerides, Low HDL)
    triglycerides = np.random.normal(195, 55, n_patients).clip(80, 480).round(1)
    hdl_cholesterol = np.random.normal(41, 7, n_patients).clip(26, 68).round(1)
    ldl_cholesterol = np.random.normal(128, 32, n_patients).clip(60, 240).round(1)
    total_cholesterol = (hdl_cholesterol + ldl_cholesterol + (triglycerides / 5.0)).round(1)
    
    # Renal Biomarkers
    serum_creatinine = np.random.normal(1.05, 0.35, n_patients).clip(0.6, 3.8).round(2)
    # CKD-EPI formula approximation for eGFR
    egfr = (141 * np.minimum(serum_creatinine / 0.9, 1.0)**(-0.411) * 
            np.maximum(serum_creatinine / 0.9, 1.0)**(-1.209) * 
            (0.993**ages)).round(1)
    uacr = np.exp(np.random.normal(3.2, 1.1, n_patients)).clip(5, 800).round(1) # mg/g albumin-to-creatinine
    
    # Hemodynamics
    systolic_bp = np.random.normal(136, 17, n_patients).clip(102, 195).astype(int)
    diastolic_bp = np.random.normal(86, 11, n_patients).clip(62, 118).astype(int)
    resting_hr = np.random.normal(76, 9, n_patients).clip(54, 108).astype(int)
    
    # Medications
    on_metformin = np.random.choice([1, 0], n_patients, p=[0.88, 0.12])
    on_sglt2i = np.random.choice([1, 0], n_patients, p=[0.42, 0.58])
    on_glimepiride = np.random.choice([1, 0], n_patients, p=[0.38, 0.62])
    on_statin = np.random.choice([1, 0], n_patients, p=[0.65, 0.35])
    on_telmisartan = np.random.choice([1, 0], n_patients, p=[0.58, 0.42])
    
    # Indian-Calibrated 10-Year ASCVD Risk Score (Modified Framingham + South Asian 1.5x Multiplier)
    ascvd_base = (
        (ages - 40) * 0.45 + 
        (systolic_bp - 120) * 0.12 + 
        (total_cholesterol - 150) * 0.08 - 
        (hdl_cholesterol - 50) * 0.15 + 
        (hba1c - 6.5) * 1.8 + 
        np.where(smoker_status == "Current", 5.5, 0.0) +
        family_history_cad * 4.0
    )
    ascvd_risk_pct = (1 / (1 + np.exp(-0.06 * ascvd_base)) * 42.0).clip(2.1, 48.0).round(2)
    
    # Diabetic Kidney Disease (DKD) Stage
    dkd_stage = np.where(egfr >= 90, "Stage 1 (Normal)",
                np.where(egfr >= 60, "Stage 2 (Mild)",
                np.where(egfr >= 30, "Stage 3 (Moderate)", "Stage 4/5 (Severe)")))
    
    # 90-Day Glycemic Decompensation Probability
    glycemic_risk_score = (1 / (1 + np.exp(-(0.7 * (hba1c - 7.5) + 0.015 * (fasting_glucose - 140) + 0.1 * diabetes_durations)))).round(3)

    df_ehr = pd.DataFrame({
        "patient_id": patient_ids,
        "age": ages,
        "gender": genders,
        "location": locations,
        "diet_type": diet_types,
        "bmi": bmis,
        "waist_cm": waist_circumference,
        "diabetes_duration_yr": diabetes_durations,
        "family_history_cad": family_history_cad,
        "smoker_status": smoker_status,
        "hba1c_pct": hba1c,
        "fasting_glucose_mgdl": fasting_glucose,
        "postprandial_glucose_mgdl": postprandial_glucose,
        "triglycerides_mgdl": triglycerides,
        "hdl_mgdl": hdl_cholesterol,
        "ldl_mgdl": ldl_cholesterol,
        "total_cholesterol_mgdl": total_cholesterol,
        "serum_creatinine_mgdl": serum_creatinine,
        "egfr_ml_min": egfr,
        "uacr_mg_g": uacr,
        "systolic_bp_mmhg": systolic_bp,
        "diastolic_bp_mmhg": diastolic_bp,
        "resting_hr_bpm": resting_hr,
        "med_metformin": on_metformin,
        "med_sglt2i": on_sglt2i,
        "med_glimepiride": on_glimepiride,
        "med_statin": on_statin,
        "med_telmisartan": on_telmisartan,
        "ascvd_10yr_risk_pct": ascvd_risk_pct,
        "dkd_stage": dkd_stage,
        "glycemic_decompensation_risk": glycemic_risk_score
    })
    
    return df_ehr

def generate_telemetry_series(patient_id="IND-PT-1001", hours=72, freq_min=5, baseline_hba1c=8.2, baseline_sbp=142):
    """
    Generates realistic 5-minute sampling interval wearable telemetry:
    - CGM (mg/dL)
    - PPG Heart Rate (bpm)
    - HRV RMSSD (ms)
    - Continuous Systolic/Diastolic BP (mmHg)
    - Step Count & Activity METs
    """
    total_steps = int(hours * 60 / freq_min)
    timestamps = pd.date_range(end=pd.Timestamp.now(), periods=total_steps, freq=f"{freq_min}min")
    
    # Circadian & Meal rhythms
    time_of_day_hours = (timestamps.hour + timestamps.minute / 60.0).values
    
    # Baseline glucose centered on baseline_hba1c
    glucose_mean = (baseline_hba1c - 5.0) * 28.0 + 95.0
    cgm_series = np.ones(total_steps) * glucose_mean
    
    # Breakfast (8:30 AM), Lunch (1:30 PM), Dinner (8:30 PM) spikes
    for i, t in enumerate(time_of_day_hours):
        meal_boost = 0.0
        # Breakfast
        if 8.5 <= t <= 11.0:
            meal_boost += 55.0 * np.sin(np.pi * (t - 8.5) / 2.5)
        # Lunch
        elif 13.5 <= t <= 16.5:
            meal_boost += 68.0 * np.sin(np.pi * (t - 13.5) / 3.0)
        # Dinner
        elif 20.5 <= t <= 23.5:
            meal_boost += 62.0 * np.sin(np.pi * (t - 20.5) / 3.0)
        # Dawn phenomenon (4:00 AM - 7:00 AM)
        elif 4.0 <= t <= 7.0:
            meal_boost += 22.0 * np.sin(np.pi * (t - 4.0) / 3.0)
            
        cgm_series[i] += meal_boost
    
    # Add autoregressive physiological noise
    ar_noise = np.zeros(total_steps)
    for i in range(1, total_steps):
        ar_noise[i] = 0.88 * ar_noise[i-1] + np.random.normal(0, 3.2)
    cgm_series = (cgm_series + ar_noise).clip(62, 385).round(1)
    
    # Heart Rate & HRV
    circadian_hr = 72 + 8 * np.sin(2 * np.pi * (time_of_day_hours - 8) / 24)
    steps_walked = np.zeros(total_steps, dtype=int)
    for i, t in enumerate(time_of_day_hours):
        if 7.0 <= t <= 8.0:  # Morning walk
            steps_walked[i] = np.random.randint(120, 280)
        elif 18.0 <= t <= 19.5:  # Evening commute / walk
            steps_walked[i] = np.random.randint(60, 220)
        elif 1.0 <= t <= 6.0:  # Sleep
            steps_walked[i] = 0
        else:
            steps_walked[i] = np.random.randint(0, 45)
            
    activity_hr_boost = (steps_walked / 20.0).clip(0, 45)
    heart_rate = (circadian_hr + activity_hr_boost + np.random.normal(0, 2.5, total_steps)).clip(48, 165).round(1)
    
    # HRV RMSSD inversely proportional to HR & stress/hyperglycemia
    hrv_rmssd = (45.0 - (heart_rate - 65.0) * 0.35 - (cgm_series - 120.0) * 0.04 + np.random.normal(0, 3.0, total_steps)).clip(12.0, 75.0).round(1)
    
    # Continuous Blood Pressure (Circadian dipping: 10-20% drop at night)
    nocturnal_dip = np.where((time_of_day_hours >= 23.0) | (time_of_day_hours <= 6.0), 12.0, 0.0)
    systolic_bp = (baseline_sbp - nocturnal_dip + (heart_rate - 72) * 0.28 + np.random.normal(0, 3.5, total_steps)).clip(95, 190).round(1)
    diastolic_bp = (systolic_bp * 0.62 + np.random.normal(0, 2.2, total_steps)).clip(58, 115).round(1)
    
    df_telemetry = pd.DataFrame({
        "timestamp": timestamps,
        "patient_id": patient_id,
        "cgm_glucose_mgdl": cgm_series,
        "heart_rate_bpm": heart_rate,
        "hrv_rmssd_ms": hrv_rmssd,
        "systolic_bp_mmhg": systolic_bp,
        "diastolic_bp_mmhg": diastolic_bp,
        "step_count": steps_walked,
        "mets_activity": (1.0 + steps_walked / 80.0).round(2)
    })
    
    return df_telemetry

def build_curated_personas():
    """Builds clinical personas for demonstration in the Streamlit app"""
    personas = [
        {
            "patient_id": "IND-PT-1001",
            "name": "Ramesh V. Sharma",
            "age": 54,
            "gender": "Male",
            "city": "Bengaluru, Karnataka",
            "diet": "South Indian Vegetarian (High Carb Rice/Idli)",
            "bmi": 27.8,
            "waist_cm": 98.5,
            "diabetes_duration_yr": 7.5,
            "hba1c": 8.6,
            "fpg": 178,
            "ppg": 262,
            "bp": "148/92 mmHg",
            "lipids": "Triglycerides: 245 mg/dL | HDL: 36 mg/dL | LDL: 142 mg/dL",
            "renal": "Serum Creatinine: 1.15 mg/dL | eGFR: 72 mL/min | UACR: 85 mg/g",
            "medications": ["Metformin 1000mg BD", "Glimepiride 2mg OD", "Telmisartan 40mg OD"],
            "phenotype": "Asian Indian Phenotype: High visceral fat, progressive beta-cell decline, nocturnal hypertension",
            "ascvd_10yr": 24.8,
            "clinical_notes": "Patient reports postprandial fatigue and erratic dawn glucose spikes. Non-dipper nocturnal BP profile detected by wearable twin."
        },
        {
            "patient_id": "IND-PT-1002",
            "name": "Priya Lakshmi Sundaram",
            "age": 48,
            "gender": "Female",
            "city": "Chennai, Tamil Nadu",
            "diet": "Vegetarian",
            "bmi": 25.2,
            "waist_cm": 86.0,
            "diabetes_duration_yr": 3.2,
            "hba1c": 7.4,
            "fpg": 138,
            "ppg": 195,
            "bp": "134/84 mmHg",
            "lipids": "Triglycerides: 178 mg/dL | HDL: 44 mg/dL | LDL: 118 mg/dL",
            "renal": "Serum Creatinine: 0.85 mg/dL | eGFR: 88 mL/min | UACR: 24 mg/g",
            "medications": ["Metformin 500mg BD", "Empagliflozin 10mg OD"],
            "phenotype": "Early cardio-metabolic syndrome with well-preserved renal function; responsive to lifestyle modification.",
            "ascvd_10yr": 11.2,
            "clinical_notes": "Well-controlled on SGLT2 inhibitor; high HRV stability. Candidate for dietary carbohydrate reduction."
        },
        {
            "patient_id": "IND-PT-1003",
            "name": "Anand S. Kulkarni",
            "age": 62,
            "gender": "Male",
            "city": "Mumbai, Maharashtra",
            "diet": "Mixed Non-Vegetarian",
            "bmi": 30.4,
            "waist_cm": 106.0,
            "diabetes_duration_yr": 14.0,
            "hba1c": 9.4,
            "fpg": 210,
            "ppg": 315,
            "bp": "162/98 mmHg",
            "lipids": "Triglycerides: 310 mg/dL | HDL: 32 mg/dL | LDL: 165 mg/dL",
            "renal": "Serum Creatinine: 1.62 mg/dL | eGFR: 46 mL/min | UACR: 312 mg/g",
            "medications": ["Metformin 1000mg BD", "Teneligliptin 20mg OD", "Telmisartan 80mg + Amlodipine 5mg", "Atorvastatin 20mg"],
            "phenotype": "Advanced Cardio-Renal-Metabolic Syndrome; microvascular renal injury and severe endothelial dysfunction.",
            "ascvd_10yr": 38.6,
            "clinical_notes": "High risk of acute cardiovascular event; persistent albuminuria (DKD Stage 3). Requires tight nocturnal BP and glucose guardrails."
        }
    ]
    return personas

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(base_dir, exist_ok=True)
    
    print("Generating 500 Indian Patient Synthetic EHR Cohort...")
    df_ehr = generate_cohort(n_patients=500, random_seed=42)
    ehr_path = os.path.join(base_dir, "patients_ehr.csv")
    df_ehr.to_csv(ehr_path, index=False)
    print(f"Saved EHR dataset to {ehr_path} (Shape: {df_ehr.shape})")
    
    print("Generating High-Frequency Wearable Telemetry Time-Series (72h @ 5min)...")
    df_telemetry = generate_telemetry_series(patient_id="IND-PT-1001", hours=72, freq_min=5, baseline_hba1c=8.6, baseline_sbp=148)
    telemetry_path = os.path.join(base_dir, "wearables_cgm_telemetry.csv")
    df_telemetry.to_csv(telemetry_path, index=False)
    print(f"Saved Telemetry dataset to {telemetry_path} (Shape: {df_telemetry.shape})")
    
    personas = build_curated_personas()
    personas_path = os.path.join(base_dir, "sample_patient_profiles.json")
    with open(personas_path, "w", encoding="utf-8") as f:
        json.dump(personas, f, indent=2)
    print(f"Saved Curated Personas to {personas_path}")

if __name__ == "__main__":
    main()
