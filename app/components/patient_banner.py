"""
CardioTwin-India: Patient Banner Component
"""

import streamlit as st

def render_patient_banner(patient):
    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 20px 24px; border: 1px solid #E2E8F0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
            <div>
                <span style="font-size: 0.85rem; background: #EEF2FF; color: #4338CA; padding: 3px 10px; border-radius: 12px; font-weight: 600;">
                    VIRTUAL PATIENT ID: {patient['patient_id']}
                </span>
                <h2 style="margin: 8px 0 4px 0; color: #0F172A; font-weight: 700; font-size: 1.6rem;">
                    {patient['name']}
                </h2>
                <p style="margin: 0; color: #64748B; font-size: 0.95rem;">
                    👤 {patient['age']} yrs • {patient['gender']} • 📍 {patient['city']} • 🥗 {patient['diet']}
                </p>
            </div>
            <div style="text-align: right; margin-top: 8px;">
                <div style="font-size: 0.8rem; color: #64748B; font-weight: 600;">METABOLIC PHENOTYPE</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #DC2626;">Asian Indian Phenotype (AIP)</div>
                <div style="font-size: 0.82rem; color: #475569;">Duration: {patient['diabetes_duration_yr']} yrs</div>
            </div>
        </div>
        <hr style="border: 0; border-top: 1px solid #F1F5F9; margin: 14px 0;">
        <div style="display: flex; flex-wrap: wrap; gap: 24px; font-size: 0.88rem;">
            <div><strong>BMI:</strong> {patient['bmi']} kg/m² <span style="color: #DC2626; font-size: 0.78rem;">(Asian Cutoff ≥25)</span></div>
            <div><strong>Waist:</strong> {patient['waist_cm']} cm</div>
            <div><strong>Baseline HbA1c:</strong> {patient['hba1c']}%</div>
            <div><strong>Clinic BP:</strong> {patient['bp']}</div>
            <div><strong>Lipid Profile:</strong> {patient['lipids']}</div>
            <div><strong>Renal Function:</strong> {patient['renal']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
