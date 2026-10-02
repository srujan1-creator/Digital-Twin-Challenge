"""
CardioTwin-India: Multi-Horizon Predictive Risk Component
Projects Short-Term (120 min), Medium-Term (90 days), and Long-Term (10 Years) outcomes.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from models.glucose_forecast_lstm import WearableSequenceForecaster
from models.ehr_risk_predictor import CardioRiskPredictor

def render_risk_forecasting(patient, df_telemetry, ehr_row):
    st.markdown("### 🔮 Multi-Horizon AI Predictive Engine")
    st.caption("Fusing high-frequency wearable sequence dynamics with static longitudinal EHR biomarkers.")
    
    forecaster = WearableSequenceForecaster()
    predictor = CardioRiskPredictor()
    predictor.load_models()
    
    preds = predictor.predict_patient(ehr_row)
    
    # Tabs for Multi-Horizon
    tab_short, tab_medium, tab_long = st.tabs([
        "⚡ Short-Term Horizon (Next 120 Mins)",
        "🗓️ Medium-Term Horizon (90-Day Decompensation)",
        "🌐 Long-Term Horizon (10-Year ASCVD & DKD)"
    ])
    
    with tab_short:
        st.markdown("#### 120-Minute Forward Glucose Trajectory & Acute Alerting")
        
        # Recent history
        recent_cgm = df_telemetry["cgm_glucose_mgdl"].iloc[-24:].values
        recent_hr = df_telemetry["heart_rate_bpm"].iloc[-24:].values
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            meal_logged = st.number_input("Simulate Imminent Meal Carbs (g)", min_value=0, max_value=100, value=0, step=10)
        with col_opt2:
            walk_scheduled = st.checkbox("Immediate 20-min Post-Meal Brisk Walk", value=False)
            
        fc = forecaster.forecast_trajectory(recent_cgm, recent_hr, meal_recent_carbs=meal_logged, exercise_active=walk_scheduled)
        
        # Display Clinical Alerts
        if fc["clinical_alerts"]:
            for alert in fc["clinical_alerts"]:
                if alert["severity"] == "CRITICAL":
                    st.error(f"🚨 **{alert['type']}**: {alert['message']}")
                else:
                    st.warning(f"⚠️ **{alert['type']}**: {alert['message']}")
        else:
            st.success("✅ **STABLE TRAJECTORY**: No acute glycemic emergencies projected over the next 120 minutes.")

        # Plot Historical + Forecast
        hist_steps = np.arange(-len(recent_cgm) * 5, 0, 5)
        future_steps = np.array(fc["future_minutes"])
        
        fig_fc = go.Figure()
        # Historical
        fig_fc.add_trace(go.Scatter(
            x=hist_steps, y=recent_cgm,
            name="Recent Wearable CGM (Past 2h)",
            line=dict(color="#475569", width=2)
        ))
        # Forecast
        fig_fc.add_trace(go.Scatter(
            x=future_steps, y=fc["forecast_glucose"],
            name="Projected Trajectory (Next 2h)",
            line=dict(color="#6366F1", width=2.8, dash="solid")
        ))
        # 95% Confidence Band
        fig_fc.add_trace(go.Scatter(
            x=list(future_steps) + list(future_steps[::-1]),
            y=fc["ci_upper_95"] + fc["ci_lower_95"][::-1],
            fill='toself',
            fillcolor='rgba(99, 102, 241, 0.15)',
            line=dict(color='rgba(255,255,255,0)'),
            name="95% Physiological Confidence Band"
        ))
        fig_fc.add_hrect(
            y0=70, y1=180, fillcolor="rgba(16, 185, 129, 0.08)", line_width=0,
            annotation_text="Target Range (70-180 mg/dL)", annotation_position="top left"
        )
        fig_fc.update_layout(
            xaxis_title="Minutes relative to Current Time (0 = Now)",
            yaxis_title="Glucose (mg/dL)",
            height=380,
            margin=dict(l=30, r=20, t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_fc, use_container_width=True)

    with tab_medium:
        st.markdown("#### 90-Day Glycemic Decompensation & HbA1c Trajectory")
        glyc_prob = preds["glycemic_decompensation_probability"]
        
        col_g1, col_g2 = st.columns([1, 1.2])
        with col_g1:
            st.metric(
                label="90-Day Decompensation Risk",
                value=f"{glyc_prob * 100:.1f}%",
                delta="High Probability" if glyc_prob > 0.4 else "Controlled",
                delta_color="inverse" if glyc_prob > 0.4 else "normal"
            )
            st.markdown(f"""
            - **Current HbA1c:** {ehr_row['hba1c_pct']}%
            - **Projected HbA1c at 90 days:** {ehr_row['hba1c_pct'] + (0.45 if glyc_prob > 0.4 else -0.2):.2f}%
            - **Beta-cell Exhaustion Index:** {'Severe' if ehr_row['diabetes_duration_yr'] > 8 else 'Moderate'}
            """)
        with col_g2:
            # Trajectory projection chart
            days = np.array([0, 30, 60, 90])
            drift = 0.5 * glyc_prob
            hba1c_baseline_curve = ehr_row['hba1c_pct'] + days * (drift / 90.0)
            hba1c_controlled_curve = ehr_row['hba1c_pct'] - days * (0.35 / 90.0)
            
            fig_hba1c = go.Figure()
            fig_hba1c.add_trace(go.Scatter(x=days, y=hba1c_baseline_curve, name="Unmanaged Trajectory", line=dict(color="#EF4444", width=2.5)))
            fig_hba1c.add_trace(go.Scatter(x=days, y=hba1c_controlled_curve, name="Digital Twin Guided Plan", line=dict(color="#10B981", width=2.5)))
            fig_hba1c.add_hline(y=7.0, line_dash="dash", line_color="#10B981", annotation_text="Target HbA1c < 7.0%")
            fig_hba1c.update_layout(
                xaxis_title="Days Forward",
                yaxis_title="Estimated HbA1c (%)",
                height=300,
                margin=dict(l=30, r=20, t=30, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_hba1c, use_container_width=True)

    with tab_long:
        st.markdown("#### 10-Year ASCVD Cardiovascular & Diabetic Kidney Disease Risk")
        c_asc1, c_asc2 = st.columns(2)
        
        with c_asc1:
            st.metric(
                label="10-Year ASCVD Risk (South Asian Calibrated)",
                value=f"{preds['ascvd_10yr_risk_pct']:.1f}%",
                delta=preds["ascvd_category"],
                delta_color="inverse" if preds['ascvd_10yr_risk_pct'] >= 20.0 else "normal"
            )
            st.caption("Calculated using Modified Framingham/ACC formula calibrated with 1.5x Asian Indian risk multiplier.")
            
            st.markdown("##### Top Patient Risk Drivers (XGBoost Attributions)")
            for feat, imp in preds["top_risk_drivers"]:
                st.progress(min(1.0, imp * 3.0), text=f"{feat.replace('_', ' ').title()}: {imp * 100:.1f}% attribution")
                
        with c_asc2:
            st.metric(
                label="Predicted DKD Progression Stage",
                value=preds["dkd_stage_prediction"],
                delta="Microalbuminuria Present" if ehr_row["uacr_mg_g"] > 30 else "Normoalbuminuric"
            )
            st.markdown("##### Stage Probability Distribution")
            fig_dkd = go.Figure(go.Bar(
                x=list(preds["dkd_stage_probabilities"].keys()),
                y=[v * 100 for v in preds["dkd_stage_probabilities"].values()],
                marker_color=["#10B981", "#F59E0B", "#EF4444", "#991B1B"][:len(preds["dkd_stage_probabilities"])]
            ))
            fig_dkd.update_layout(
                yaxis_title="Probability (%)",
                height=260,
                margin=dict(l=30, r=20, t=20, b=30)
            )
            st.plotly_chart(fig_dkd, use_container_width=True)
