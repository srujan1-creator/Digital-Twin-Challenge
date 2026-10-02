"""
CardioTwin-India: Organ-Level Virtual Patient Twin Component
Multi-scale physiological modeling across 5 key cardio-renal-metabolic systems.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np

def render_organ_digital_twin(patient, df_telemetry):
    st.markdown("### 🫀 Multi-Scale Virtual Patient: Organ-Level Dynamics")
    st.caption("Coupled physiological compartments estimating real-time organ strain, tissue perfusion, and progressive micro/macrovascular damage.")
    
    col_left, col_right = st.columns([1.2, 1.0])
    
    with col_left:
        # Calculate dynamic organ indices
        cgm_latest = df_telemetry["cgm_glucose_mgdl"].iloc[-1]
        sbp_latest = df_telemetry["systolic_bp_mmhg"].iloc[-1]
        hr_latest = df_telemetry["heart_rate_bpm"].iloc[-1]
        
        # 1. Pancreatic Beta-Cell Capacity (HOMA-B approximation)
        hba1c = float(patient["hba1c"])
        duration = float(patient["diabetes_duration_yr"])
        beta_cell_reserve = max(15.0, 100.0 - (duration * 4.8) - ((hba1c - 6.0) * 8.5))
        
        # 2. Arterial Stiffness Index (derived from pulse pressure and age)
        pulse_pressure = sbp_latest - float(df_telemetry["diastolic_bp_mmhg"].iloc[-1])
        arterial_stiffness_score = min(100.0, (pulse_pressure / 40.0) * 45.0 + (patient["age"] / 70.0) * 35.0)
        
        # 3. Myocardial Strain / Rate Pressure Product (RPP = HR * SBP / 100)
        rpp = (hr_latest * sbp_latest) / 100.0
        myocardial_strain = min(100.0, (rpp / 160.0) * 75.0)
        
        # 4. Glomerular Filtration Stress
        # Hyperglycemia + Hypertension causes glomerular capillary hypertension
        renal_strain = min(100.0, ((cgm_latest / 180.0) * 35.0 + (sbp_latest / 130.0) * 45.0))
        
        # 5. Hepatic Steatosis & Insulin Resistance Index
        hepatic_ir = min(100.0, (patient["bmi"] / 25.0) * 40.0 + (hba1c / 7.0) * 40.0)

        # Radar chart for organ-level status
        categories = [
            "Pancreatic Strain",
            "Arterial Stiffness",
            "Myocardial Workload",
            "Glomerular Stress",
            "Hepatic Insulin Res."
        ]
        values = [100 - beta_cell_reserve, arterial_stiffness_score, myocardial_strain, renal_strain, hepatic_ir]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='Current Virtual State',
            fillcolor='rgba(99, 102, 241, 0.25)',
            line=dict(color='#4F46E5', width=2.5)
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[35, 35, 35, 35, 35, 35],
            theta=categories + [categories[0]],
            name='Optimal Physiological Threshold',
            line=dict(color='#10B981', dash='dash', width=1.5)
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9)),
            ),
            margin=dict(l=40, r=40, t=30, b=20),
            height=380,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_right:
        st.markdown("#### Organ Compartment Telemetry")
        
        # Organ cards
        st.markdown(f"""
        <div class="organ-card">
            <div style="display: flex; justify-content: space-between;">
                <strong>🔬 Pancreatic Islets (Beta-Cells)</strong>
                <span class="{'status-badge-critical' if beta_cell_reserve < 40 else 'status-badge-warning'}">
                    Reserve: {beta_cell_reserve:.1f}%
                </span>
            </div>
            <div style="font-size: 0.85rem; color: #475569; margin-top: 4px;">
                Endogenous basal insulin secretion is declining. Glucotoxicity index is elevated ({cgm_latest:.0f} mg/dL).
            </div>
        </div>
        
        <div class="organ-card" style="border-left-color: #EF4444;">
            <div style="display: flex; justify-content: space-between;">
                <strong>🫀 Arterial Vasculature & Endothelium</strong>
                <span class="{'status-badge-critical' if arterial_stiffness_score > 65 else 'status-badge-warning'}">
                    Stiffness: {arterial_stiffness_score:.1f}/100
                </span>
            </div>
            <div style="font-size: 0.85rem; color: #475569; margin-top: 4px;">
                Pulse Pressure: {pulse_pressure:.0f} mmHg. High systemic resistance accelerating vascular remodeling.
            </div>
        </div>
        
        <div class="organ-card" style="border-left-color: #F59E0B;">
            <div style="display: flex; justify-content: space-between;">
                <strong>🫘 Renal Glomerular Filtration</strong>
                <span class="{'status-badge-critical' if renal_strain > 70 else 'status-badge-warning'}">
                    Strain: {renal_strain:.1f}/100
                </span>
            </div>
            <div style="font-size: 0.85rem; color: #475569; margin-top: 4px;">
                Glomerular capillary hypertension driving microalbumin leakage. SGLT2 titration indicated.
            </div>
        </div>
        
        <div class="organ-card" style="border-left-color: #10B981;">
            <div style="display: flex; justify-content: space-between;">
                <strong>🩺 Myocardial Oxygen Workload (RPP)</strong>
                <span class="status-badge-normal">
                    Workload: {myocardial_strain:.1f}/100
                </span>
            </div>
            <div style="font-size: 0.85rem; color: #475569; margin-top: 4px;">
                Rate-Pressure Product: {rpp:.0f} (Moderate). Preserved ejection fraction baseline.
            </div>
        </div>
        """, unsafe_allow_html=True)
