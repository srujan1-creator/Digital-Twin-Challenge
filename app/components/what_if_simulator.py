"""
CardioTwin-India: Counterfactual 'What-If' Simulation Component
Simulates physiological responses to personalized lifestyle and pharmacological interventions.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from models.physiological_sim import BergmanGlucoseInsulinModel, WindkesselHemodynamicModel

def render_what_if_simulator(patient):
    st.markdown("### 🧪 Counterfactual 'What-If' Clinical Simulator")
    st.caption("Interactive in-silico simulation: test dietary modifications, exercise regimens, and drug titrations before prescribing.")
    
    bergman = BergmanGlucoseInsulinModel()
    windkessel = WindkesselHemodynamicModel(
        baseline_sbp=float(patient["bp"].split("/")[0]),
        baseline_dbp=float(patient["bp"].split("/")[1].replace(" mmHg", ""))
    )
    
    # Intervention Controls
    c_ctrl1, c_ctrl2, c_ctrl3 = st.columns(3)
    
    with c_ctrl1:
        st.markdown("##### 🥗 Nutritional Intervention")
        carb_reduction = st.slider(
            "Refined Carb Reduction (Swapping Rice for Millets/Fiber)",
            min_value=0, max_value=50, value=25, step=5,
            format="%d%%"
        )
        meal_size_g = st.number_input("Meal Carbohydrate Load (g)", min_value=30, max_value=120, value=75, step=5)
        
    with c_ctrl2:
        st.markdown("##### 🏃 Lifestyle & Activity")
        exercise_mins = st.slider(
            "Postprandial Brisk Walk (Minutes)",
            min_value=0, max_value=45, value=20, step=5,
            help="Stimulates insulin-independent GLUT4 glucose uptake in skeletal muscle."
        )
        
    with c_ctrl3:
        st.markdown("##### 💊 Pharmacotherapy Titration")
        titrate_sglt2i = st.checkbox("Add SGLT2i (Empagliflozin 10mg)", value=True, help="Promotes renal glucose excretion and lowers preload")
        titrate_arb = st.checkbox("Bedtime Telmisartan (Chronotherapy)", value=True, help="Restores nocturnal dipping blood pressure profile")

    # Run Numerical ODE Simulations
    # 1. Baseline Simulation (Current uncontrolled state)
    sim_baseline = bergman.simulate(
        initial_glucose=float(patient["fpg"]),
        meal_carbs_g=meal_size_g,
        carb_absorption_rate=1.0,
        exercise_active=False,
        med_metformin=True,
        med_sglt2i=False,
        minutes=240
    )
    
    # 2. Counterfactual Intervention Simulation
    reduced_carbs = meal_size_g * (1.0 - (carb_reduction / 100.0))
    sim_intervention = bergman.simulate(
        initial_glucose=float(patient["fpg"]),
        meal_carbs_g=reduced_carbs,
        carb_absorption_rate=0.75 if carb_reduction >= 20 else 1.0,
        exercise_active=exercise_mins >= 15,
        med_metformin=True,
        med_sglt2i=titrate_sglt2i,
        minutes=240
    )
    
    # Hemodynamic 24h simulation
    bp_baseline = windkessel.simulate_24h_cycle(nocturnal_dipping_impaired=True, arb_titrated=False, aerobic_activity_hrs=0.0)
    bp_intervention = windkessel.simulate_24h_cycle(
        nocturnal_dipping_impaired=not titrate_arb,
        arb_titrated=titrate_arb,
        aerobic_activity_hrs=exercise_mins / 60.0
    )

    # In-Silico Outcomes Dashboard
    st.markdown("---")
    st.markdown("#### 📊 Simulated In-Silico Outcomes")
    
    m1, m2, m3, m4 = st.columns(4)
    peak_diff = sim_baseline["peak_glucose"] - sim_intervention["peak_glucose"]
    tir_diff = sim_intervention["time_in_range_pct"] - sim_baseline["time_in_range_pct"]
    sbp_diff = bp_baseline["mean_night_sbp"] - bp_intervention["mean_night_sbp"]
    
    with m1:
        st.metric(
            label="Peak Glucose Surge",
            value=f"{sim_intervention['peak_glucose']:.1f} mg/dL",
            delta=f"-{peak_diff:.1f} mg/dL (Blunted)",
            delta_color="normal"
        )
    with m2:
        st.metric(
            label="Time in Range (70-180)",
            value=f"{sim_intervention['time_in_range_pct']:.1f}%",
            delta=f"+{tir_diff:.1f}% TIR",
            delta_color="normal"
        )
    with m3:
        st.metric(
            label="Nocturnal SBP",
            value=f"{bp_intervention['mean_night_sbp']:.0f} mmHg",
            delta=f"-{sbp_diff:.1f} mmHg",
            delta_color="normal"
        )
    with m4:
        st.metric(
            label="Ambulatory Dipping Pattern",
            value=bp_intervention["dipper_status"].split()[0],
            delta=f"Ratio: {bp_intervention['dipping_ratio_pct']:.1f}%"
        )

    # Visualizing Curves
    plot_col1, plot_col2 = st.columns(2)
    
    with plot_col1:
        st.markdown("###### Postprandial Glucose Response (Bergman Minimal Model)")
        fig_g = go.Figure()
        fig_g.add_trace(go.Scatter(
            x=sim_baseline["time_minutes"], y=sim_baseline["glucose_mgdl"],
            name="Baseline (Standard High Carb)",
            line=dict(color="#EF4444", width=2.5, dash="dash")
        ))
        fig_g.add_trace(go.Scatter(
            x=sim_intervention["time_minutes"], y=sim_intervention["glucose_mgdl"],
            name="Counterfactual Twin Intervention",
            line=dict(color="#10B981", width=3)
        ))
        fig_g.add_hrect(
            y0=70, y1=180,
            fillcolor="rgba(16, 185, 129, 0.1)", line_width=0,
            annotation_text="Target Range", annotation_position="bottom right"
        )
        fig_g.update_layout(
            xaxis_title="Minutes Post-Meal",
            yaxis_title="Plasma Glucose (mg/dL)",
            height=340,
            margin=dict(l=30, r=20, t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_g, use_container_width=True)

    with plot_col2:
        st.markdown("###### 24-Hour Ambulatory Blood Pressure Profile (Windkessel Model)")
        fig_bp = go.Figure()
        fig_bp.add_trace(go.Scatter(
            x=bp_baseline["hours"], y=bp_baseline["systolic_bp"],
            name="Baseline Non-Dipping SBP",
            line=dict(color="#F97316", width=2, dash="dash")
        ))
        fig_bp.add_trace(go.Scatter(
            x=bp_intervention["hours"], y=bp_intervention["systolic_bp"],
            name="Restored Dipping Profile",
            line=dict(color="#06B6D4", width=2.5)
        ))
        # Highlight Night Period (23:00 to 06:00)
        fig_bp.add_vrect(
            x0=0, x1=6, fillcolor="rgba(99, 102, 241, 0.08)", line_width=0,
            annotation_text="Sleep (Nocturnal Dip)", annotation_position="top left"
        )
        fig_bp.add_vrect(
            x0=23, x1=24, fillcolor="rgba(99, 102, 241, 0.08)", line_width=0
        )
        fig_bp.update_layout(
            xaxis_title="Time of Day (Hours)",
            yaxis_title="Systolic BP (mmHg)",
            height=340,
            margin=dict(l=30, r=20, t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bp, use_container_width=True)
