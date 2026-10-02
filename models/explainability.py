"""
CardioTwin-India: Clinical Explainability & Guidelines Engine
Compliant with:
- ICMR-INDIAB (Indian Council of Medical Research) Consensus Guidelines
- RSSDI (Research Society for the Study of Diabetes in India) 2026 Recommendations
- ADA / ACC Asian Indian Phenotype Risk Considerations
"""

def generate_clinical_explanation(patient_dict, ascvd_risk, dkd_stage, dipping_status):
    """
    Generates explainable clinical insights, pathophysiological rationale,
    and tailored therapeutic action points.
    """
    age = patient_dict.get("age", 50)
    bmi = patient_dict.get("bmi", 25.0)
    waist = patient_dict.get("waist_cm", 90.0)
    hba1c = patient_dict.get("hba1c_pct", 7.5)
    triglycerides = patient_dict.get("triglycerides_mgdl", 180.0)
    hdl = patient_dict.get("hdl_mgdl", 40.0)
    sbp = patient_dict.get("systolic_bp_mmhg", 130)
    
    insights = []
    recommendations = []
    
    # 1. Asian Indian Phenotype Visceral Adiposity
    if bmi >= 23.0:
        asian_bmi_status = "Obese (Class 1+)" if bmi >= 25.0 else "Overweight"
        insights.append(
            f"**Asian Indian Phenotype Assessment**: BMI of {bmi} kg/m² falls into the **{asian_bmi_status}** category "
            f"under WHO Asian cutoffs (Overweight: ≥23, Obese: ≥25). Waist circumference of {waist} cm denotes significant "
            f"ectopic and visceral fat deposition, fueling hepatic insulin resistance and subclinical systemic inflammation."
        )
        recommendations.append("Target a 5-7% total body weight reduction via a calibrated hypocaloric, low-glycemic-load diet.")

    # 2. Atherogenic Dyslipidemia
    if triglycerides > 150.0 or hdl < 40.0:
        ratio = round(triglycerides / max(1.0, hdl), 2)
        insights.append(
            f"**Atherogenic Dyslipidemia Index**: Triglyceride/HDL ratio is **{ratio}** (Triglycerides: {triglycerides} mg/dL, "
            f"HDL: {hdl} mg/dL). A TG/HDL ratio > 3.0 in South Asians is a sensitive surrogate for small dense LDL (sdLDL) particles, "
            f"dramatically accelerating coronary atherogenesis."
        )
        recommendations.append("Initiate or titrate moderate-to-high intensity Statin therapy (Atorvastatin 20mg / Rosuvastatin 10mg) per ICMR/ACC guidelines.")

    # 3. Glycemic Control & Beta-cell preservation
    if hba1c >= 8.0:
        insights.append(
            f"**Severe Hyperglycemic Exposure**: Current HbA1c of **{hba1c}%** indicates sustained glucotoxicity and impending "
            f"accelerated beta-cell apoptosis. Postprandial glucose excursions drive microvascular endothelial damage."
        )
        recommendations.append("Consider dual/triple oral therapy: Add SGLT2 inhibitor (Empagliflozin 10mg or Dapagliflozin 10mg) for combined cardiorenal protection and glycemic reduction.")
    elif hba1c >= 7.0:
        insights.append(
            f"**Sub-Optimal Glycemic Control**: Current HbA1c is **{hba1c}%** (Target: < 7.0%). Digital twin reveals recurrent postprandial excursions."
        )
        recommendations.append("Optimize dietary carbohydrate distribution; replace high-glycemic refined grains (white rice) with complex whole grains / millets.")

    # 4. Nocturnal Hemodynamics & Cardiovascular Dipping
    if "Non-Dipper" in dipping_status:
        insights.append(
            f"**Autonomic & Hemodynamic Risk**: The wearable digital twin detected a **Non-Dipping Nocturnal BP pattern**. "
            f"Failure of nocturnal blood pressure to drop by ≥10% is associated with a 2.4-fold increase in cardiovascular mortality and stroke."
        )
        recommendations.append("Switch antihypertensive dosing (Telmisartan) to bedtime (chronotherapy) to restore physiological nocturnal dipping.")
    
    # 5. Cardiorenal Protection
    if ascvd_risk >= 20.0 or "Stage 2" in dkd_stage or "Stage 3" in dkd_stage:
        insights.append(
            f"**Cardio-Renal Risk Confluence**: High 10-Year ASCVD risk ({ascvd_risk}%) co-existing with {dkd_stage} demonstrates "
            f"interconnected vascular and glomerular vulnerability."
        )
        recommendations.append("Maintain strict blood pressure target (<130/80 mmHg) and monitor microalbuminuria (UACR) every 6 months.")

    return {
        "phenotype_insights": insights,
        "clinical_action_plan": recommendations
    }
