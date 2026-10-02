"""
CardioTwin-India: A Multimodal Physiomarker Digital Twin for Predictive Cardio-Metabolic & Type 2 Diabetes Management
Official Submission for Happiest Health - Digital Twin Challenge 2026
"Reimagining & Reforming Healthcare in India Summit 2026"
"""

import os
import sys
import json
import streamlit as st
import pandas as pd
import numpy as np

# Add project root to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.components.patient_banner import render_patient_banner
from app.components.real_time_telemetry import render_telemetry_dashboard
from app.components.organ_digital_twin import render_organ_digital_twin
from app.components.what_if_simulator import render_what_if_simulator
from app.components.risk_forecasting import render_risk_forecasting
from app.components.fhir_exporter import render_fhir_export
from models.explainability import generate_clinical_explanation
from models.ehr_risk_predictor import CardioRiskPredictor
from models.physiological_sim import WindkesselHemodynamicModel

# Page Configuration
st.set_page_config(
    page_title="CardioTwin-India | Digital Twin Challenge 2026",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Data Loading Cache
@st.cache_data
def load_datasets():
    data_dir = os.path.join(root_dir, "data")
    ehr_path = os.path.join(data_dir, "patients_ehr.csv")
    telemetry_path = os.path.join(data_dir, "wearables_cgm_telemetry.csv")
    personas_path = os.path.join(data_dir, "sample_patient_profiles.json")
    
    df_ehr = pd.read_csv(ehr_path)
    df_telemetry = pd.read_csv(telemetry_path)
    df_telemetry["timestamp"] = pd.to_datetime(df_telemetry["timestamp"])
    with open(personas_path, "r", encoding="utf-8") as f:
        personas = json.load(f)
    return df_ehr, df_telemetry, personas

df_ehr, df_telemetry, personas = load_datasets()

# Top Header
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 class="main-title">CardioTwin-India 🫀</h1>
            <div class="main-subtitle">
                A Multimodal Virtual Patient Digital Twin for Type-2 Diabetes & Cardio-Metabolic Progression in India
            </div>
            <div>
                <span class="badge-tag">🏆 Happiest Health Challenge 2026</span>
                <span class="badge-tag">🇮🇳 ICMR-INDIAB Aligned</span>
                <span class="badge-tag">🔬 Multi-Scale ODE + XGBoost</span>
                <span class="badge-tag">🏥 HL7 FHIR R4 Ready</span>
            </div>
        </div>
        <div style="text-align: right; background: rgba(255,255,255,0.08); padding: 12px 18px; border-radius: 12px;">
            <div style="font-size: 0.82rem; color: #94A3B8;">ORGANIZED BY</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #38BDF8;">Happiest Health</div>
            <div style="font-size: 0.78rem; color: #E2E8F0;">Reimagining & Reforming Healthcare Summit</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Patient Selection & Navigation
st.sidebar.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=64)
st.sidebar.title("Digital Twin Control")

patient_names = [f"{p['name']} ({p['patient_id']})" for p in personas]
selected_idx = st.sidebar.selectbox(
    "👤 Select Virtual Patient Persona",
    range(len(patient_names)),
    format_func=lambda i: patient_names[i]
)
selected_patient = personas[selected_idx]

# Match with EHR row
ehr_row = df_ehr[df_ehr["patient_id"] == selected_patient["patient_id"]]
if ehr_row.empty:
    ehr_row = df_ehr.iloc[0]
else:
    ehr_row = ehr_row.iloc[0]

# Navigation
st.sidebar.markdown("---")
st.sidebar.subheader("Navigation")
menu_choice = st.sidebar.radio(
    "Go to Module:",
    [
        "📊 Live Digital Twin & Telemetry",
        "🫀 Organ-Level Virtual Dynamics",
        "🧪 Counterfactual 'What-If' Simulator",
        "🔮 Multi-Horizon AI Predictive Engine",
        "🩺 Clinical Insights & Guidelines",
        "🏥 FHIR R4 Interoperability & Export",
        "📑 Project Architecture & Submission Info"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**Team Details:**  
- **Lead:** Kandanala Kota Mohith Srujan  
- **Email:** kandanalasrujan@gmail.com  
- **GitHub:** [Digital-Twin-Challenge](https://github.com/srujan1-creator/Digital-Twin-Challenge.git)  
- **License:** MIT Open Source  
""")

# Render Patient Demographics Banner across all tabs
render_patient_banner(selected_patient)

# Routing
if menu_choice == "📊 Live Digital Twin & Telemetry":
    render_telemetry_dashboard(df_telemetry)
    st.markdown("---")
    render_organ_digital_twin(selected_patient, df_telemetry)

elif menu_choice == "🫀 Organ-Level Virtual Dynamics":
    render_organ_digital_twin(selected_patient, df_telemetry)

elif menu_choice == "🧪 Counterfactual 'What-If' Simulator":
    render_what_if_simulator(selected_patient)

elif menu_choice == "🔮 Multi-Horizon AI Predictive Engine":
    render_risk_forecasting(selected_patient, df_telemetry, ehr_row)

elif menu_choice == "🩺 Clinical Insights & Guidelines":
    st.markdown("### 🩺 Clinical Rationale, Phenotypic Insights & Guidelines")
    
    predictor = CardioRiskPredictor()
    predictor.load_models()
    preds = predictor.predict_patient(ehr_row)
    
    windkessel = WindkesselHemodynamicModel(
        baseline_sbp=float(selected_patient["bp"].split("/")[0]),
        baseline_dbp=float(selected_patient["bp"].split("/")[1].replace(" mmHg", ""))
    )
    hemo = windkessel.simulate_24h_cycle(nocturnal_dipping_impaired=True)
    
    explanation = generate_clinical_explanation(
        ehr_row.to_dict(),
        ascvd_risk=preds["ascvd_10yr_risk_pct"],
        dkd_stage=preds["dkd_stage_prediction"],
        dipping_status=hemo["dipper_status"]
    )
    
    col_ins, col_act = st.columns(2)
    with col_ins:
        st.markdown("#### 🧬 Asian Indian Phenotype Insights")
        for ins in explanation["phenotype_insights"]:
            st.info(ins)
            
    with col_act:
        st.markdown("#### 📋 Recommended Clinical Action Plan")
        for idx, act in enumerate(explanation["clinical_action_plan"], 1):
            st.markdown(f"**{idx}.** {act}")
            
    st.markdown("---")
    st.markdown("#### 📚 Clinical Guideline Alignment")
    st.markdown("""
    - **ICMR-INDIAB Consensus (2023-2026):** Recommends tailored BMI threshold (≥23 kg/m² overweight, ≥25 kg/m² obese) and aggressive management of atherogenic dyslipidemia (TG/HDL ratio).
    - **RSSDI Guidelines (2026):** Advocates early dual/triple combination oral therapy with SGLT2 inhibitors and Metformin for patients with high visceral adiposity.
    - **Ambulatory Blood Pressure Monitoring (ABPM):** Emphasizes detection of nocturnal non-dipping (<10% dip) which is highly prevalent in South Asians with metabolic syndrome.
    """)

elif menu_choice == "🏥 FHIR R4 Interoperability & Export":
    render_fhir_export(selected_patient)

elif menu_choice == "📑 Project Architecture & Submission Info":
    st.markdown("### 📑 Project Architecture & Competition Documentation")
    
    st.markdown("""
    #### Happiest Health - Digital Twin Challenge 2026 Submission
    - **Project Title:** CardioTwin-India: A Multimodal Physiomarker Digital Twin for Predictive Cardio-Metabolic & Type 2 Diabetes Management
    - **Team Details:** Kandanala Kota Mohith Srujan (`kandanalasrujan@gmail.com`)
    - **College / Institutional Affiliation:** Indian Institute of Information Technology / Engineering Division
    - **Use Case:** Chronic cardio-metabolic disease modeling (Type 2 Diabetes, Nocturnal Hypertension, Diabetic Kidney Disease, ASCVD risk) in Indian populations.
    - **Technical Stack:** Python 3.11, Streamlit, SciPy ODE Solvers, XGBoost, Scikit-Learn, Plotly, FastAPI, HL7 FHIR R4.
    
    ---
    #### Multi-Scale Digital Twin Architecture Flow
    ```
    ┌─────────────────────────┐       ┌─────────────────────────┐
    │  Static Longitudinal    │       │ High-Frequency Dynamic  │
    │  EHR Biomarkers (ICMR)  │       │ Wearables (CGM/PPG/cBP) │
    └────────────┬────────────┘       └────────────┬────────────┘
                 │                                 │
                 └───────────────┬─────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Data Fusion & Alignment │
                    │ (Missing Imputation,    │
                    │  Circadian Normalizer)  │
                    └────────────┬────────────┘
                                 ▼
         ┌───────────────────────────────────────────────┐
         │     Multimodal Digital Twin Virtual Engine    │
         │  ├─ Bergman Minimal Model (ODE Glucose-Ins.)  │
         │  ├─ 2-Element Windkessel (Arterial Hemodyn.)  │
         │  ├─ Multi-Horizon Forecaster (120m Trajectory)│
         │  └─ XGBoost Multi-Target Risk (ASCVD/DKD/HbA1c│
         └───────────────────────┬───────────────────────┘
                                 ▼
         ┌───────────────────────────────────────────────┐
         │     Interactive Twin Interface & Services     │
         │  ├─ Real-Time Live Telemetry & Organ Strain   │
         │  ├─ Counterfactual 'What-If' Simulation Engine│
         │  ├─ Clinical Explainability (Asian Phenotype) │
         │  └─ HL7 FHIR R4 Bundle Export / ABDM Ready    │
         └───────────────────────────────────────────────┘
    ```
    """)
    
    # Download link for Architecture diagram & Presentation
    arch_pdf_path = os.path.join(root_dir, "docs", "architecture", "CardioTwin_Architecture_Diagram.pdf")
    pres_pptx_path = os.path.join(root_dir, "presentation", "CardioTwin_India_Happiest_Health_Summit_2026.pptx")
    
    c_dl1, c_dl2 = st.columns(2)
    with c_dl1:
        if os.path.exists(arch_pdf_path):
            with open(arch_pdf_path, "rb") as f:
                st.download_button(
                    label="📄 Download Architecture Diagram (PDF)",
                    data=f.read(),
                    file_name="CardioTwin_Architecture_Diagram.pdf",
                    mime="application/pdf"
                )
    with c_dl2:
        if os.path.exists(pres_pptx_path):
            with open(pres_pptx_path, "rb") as f:
                st.download_button(
                    label="📊 Download Summit Presentation (PPTX)",
                    data=f.read(),
                    file_name="CardioTwin_India_Happiest_Health_Summit_2026.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
