"""
CardioTwin-India: Real-Time Multimodal Telemetry Component
Renders CGM, PPG Heart Rate, HRV, and Blood Pressure streams.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def render_telemetry_dashboard(df_telemetry):
    st.markdown("### 📡 Real-Time Multimodal Wearable Streams (72-Hour Continuous Window)")
    st.caption("Continuous fusion of CGM sensor telemetry, PPG wrist photoplethysmography, and arterial pulse wave hemodynamics.")
    
    # Summary Metrics Row
    c1, c2, c3, c4, c5 = st.columns(5)
    
    latest = df_telemetry.iloc[-1]
    mean_glucose = df_telemetry["cgm_glucose_mgdl"].mean()
    tir = (df_telemetry["cgm_glucose_mgdl"].between(70, 180).mean()) * 100
    mean_hr = df_telemetry["heart_rate_bpm"].mean()
    mean_sbp = df_telemetry["systolic_bp_mmhg"].mean()
    mean_dbp = df_telemetry["diastolic_bp_mmhg"].mean()
    
    with c1:
        st.metric(
            label="Current CGM Glucose",
            value=f"{latest['cgm_glucose_mgdl']:.0f} mg/dL",
            delta=f"{latest['cgm_glucose_mgdl'] - df_telemetry.iloc[-5]['cgm_glucose_mgdl']:.1f} mg/dL / 20m"
        )
    with c2:
        st.metric(
            label="Time in Range (70-180)",
            value=f"{tir:.1f}%",
            delta="Below Target 70%" if tir < 70 else "Normal",
            delta_color="inverse" if tir < 70 else "normal"
        )
    with c3:
        st.metric(
            label="Wearable PPG Pulse",
            value=f"{latest['heart_rate_bpm']:.0f} bpm",
            delta=f"Avg {mean_hr:.0f} bpm"
        )
    with c4:
        st.metric(
            label="Ambulatory BP",
            value=f"{latest['systolic_bp_mmhg']:.0f}/{latest['diastolic_bp_mmhg']:.0f}",
            delta="Stage 1 HTN" if latest['systolic_bp_mmhg'] > 130 else "Optimal",
            delta_color="inverse" if latest['systolic_bp_mmhg'] > 130 else "normal"
        )
    with c5:
        st.metric(
            label="Autonomic Tone (HRV)",
            value=f"{latest['hrv_rmssd_ms']:.1f} ms",
            delta="Depressed RMSSD" if latest['hrv_rmssd_ms'] < 25 else "Balanced"
        )

    # Multi-Stream Interactive Plot
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            "Continuous Glucose Monitoring (CGM) with Target Glycemic Bands",
            "Continuous Estimated Blood Pressure & Circadian Dipping Profile",
            "PPG Heart Rate (BPM) & Autonomic Heart Rate Variability (RMSSD)"
        ),
        row_heights=[0.42, 0.32, 0.26]
    )

    # 1. CGM Stream
    time_series = df_telemetry["timestamp"]
    fig.add_trace(
        go.Scatter(
            x=time_series, y=df_telemetry["cgm_glucose_mgdl"],
            name="CGM Glucose",
            line=dict(color="#6366F1", width=2.2),
            hovertemplate="%{y:.1f} mg/dL<br>%{x}"
        ),
        row=1, col=1
    )
    # Target Glycemic Band (70 to 180)
    fig.add_hrect(
        y0=70, y1=180, row=1, col=1,
        fillcolor="rgba(16, 185, 129, 0.12)", line_width=0,
        annotation_text="Target Range (70-180 mg/dL)", annotation_position="top left",
        annotation_font_size=10, annotation_font_color="#059669"
    )
    # Severe Hyperglycemia Threshold (>250)
    fig.add_hline(y=250, row=1, col=1, line_dash="dash", line_color="#EF4444", line_width=1.2, annotation_text="Severe Spike (>250)", annotation_font_size=9)
    # Hypoglycemia Threshold (<70)
    fig.add_hline(y=70, row=1, col=1, line_dash="dash", line_color="#DC2626", line_width=1.2, annotation_text="Hypoglycemia (<70)", annotation_font_size=9)

    # 2. Blood Pressure Stream
    fig.add_trace(
        go.Scatter(
            x=time_series, y=df_telemetry["systolic_bp_mmhg"],
            name="Systolic BP",
            line=dict(color="#EF4444", width=1.8),
            hovertemplate="%{y:.0f} mmHg"
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=time_series, y=df_telemetry["diastolic_bp_mmhg"],
            name="Diastolic BP",
            line=dict(color="#F97316", width=1.4, dash="dot"),
            hovertemplate="%{y:.0f} mmHg"
        ),
        row=2, col=1
    )
    fig.add_hline(y=130, row=2, col=1, line_dash="dot", line_color="#94A3B8", line_width=1, annotation_text="ACC/AHA 130 mmHg SBP Target", annotation_font_size=9)

    # 3. Heart Rate & HRV
    fig.add_trace(
        go.Scatter(
            x=time_series, y=df_telemetry["heart_rate_bpm"],
            name="PPG Heart Rate",
            line=dict(color="#EC4899", width=1.5),
            hovertemplate="%{y:.0f} bpm"
        ),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=time_series, y=df_telemetry["hrv_rmssd_ms"],
            name="HRV RMSSD",
            line=dict(color="#06B6D4", width=1.5, dash="dash"),
            hovertemplate="%{y:.1f} ms"
        ),
        row=3, col=1
    )

    fig.update_layout(
        height=680,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
