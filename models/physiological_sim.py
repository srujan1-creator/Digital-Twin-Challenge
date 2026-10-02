"""
CardioTwin-India: Physiological Modeling Engine
Implements:
1. Bergman Minimal Model of Glucose-Insulin Dynamics (ODEs)
2. 2-Element Windkessel Cardiovascular Hemodynamics
3. Counterfactual 'What-If' Simulation (Diet, Exercise, Pharmacotherapy)
"""

import numpy as np
from scipy.integrate import odeint

class BergmanGlucoseInsulinModel:
    """
    Bergman Minimal Model with gut absorption & medication dynamics.
    Parameters calibrated for South Asian / Indian insulin-resistant phenotype.
    """
    def __init__(self, p1=0.028, p2=0.025, p3=0.000013, Gb=95.0, Ib=11.0, V=12.0):
        # p1: Glucose effectiveness (rate at which glucose clears independent of insulin)
        # p2: Rate of clearance of active insulin
        # p3: Insulin sensitivity index (often significantly lower in Asian Indians)
        # Gb: Basal glucose (mg/dL)
        # Ib: Basal insulin (mU/L)
        # V: Volume of distribution (L)
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.Gb = Gb
        self.Ib = Ib
        self.V = V

    def _derivatives(self, state, t, carb_input, carb_rate, exercise_factor, sglt2_factor):
        G, X, I = state
        
        # Meal Glucose Appearance Rate D(t)
        # Modeled as gastrointestinal absorption curve peaking around 45 min
        D_t = 0.0
        if 0 <= t <= 240:
            peak_time = 45.0
            spread = 32.0
            D_t = carb_input * carb_rate * 0.12 * np.exp(-((t - peak_time) / spread)**2)
        
        # Exercise accelerates non-insulin-mediated glucose uptake (GLUT4 translocation)
        effective_p1 = self.p1 * (1.0 + 1.2 * exercise_factor)
        
        # SGLT2 Inhibitor renal clearance threshold (reduces renal reabsorption from 180 to ~90 mg/dL)
        sglt2_renal_clearance = 0.0
        if sglt2_factor > 0:
            threshold = 100.0
            if G > threshold:
                sglt2_renal_clearance = 0.025 * sglt2_factor * (G - threshold)
        
        # dG/dt = -(p1 + X)*G + p1*Gb + D(t) - SGLT2_clearance
        dG_dt = -(effective_p1 + X) * G + effective_p1 * self.Gb + D_t - sglt2_renal_clearance
        
        # dX/dt = -p2*X + p3*(I - Ib)
        dX_dt = -self.p2 * X + self.p3 * max(0.0, I - self.Ib)
        
        # dI/dt: Pancreatic beta-cell response to elevated glucose
        beta_cell_gain = 0.05
        dI_dt = -0.05 * (I - self.Ib) + beta_cell_gain * max(0.0, G - self.Gb)
        
        return [dG_dt, dX_dt, dI_dt]

    def simulate(self, initial_glucose=140.0, meal_carbs_g=75.0, 
                 carb_absorption_rate=1.0, exercise_active=False,
                 med_metformin=True, med_sglt2i=False, minutes=240):
        """
        Runs numerical integration of the virtual patient over time horizon.
        """
        t = np.linspace(0, minutes, minutes)
        
        # Medication modulation of physiological parameters
        p3_adj = self.p3 * (1.35 if med_metformin else 1.0)
        sglt2_val = 1.0 if med_sglt2i else 0.0
        exercise_val = 1.0 if exercise_active else 0.0
        
        state0 = [initial_glucose, 0.0, self.Ib]
        
        # Save temporary parameter
        orig_p3 = self.p3
        self.p3 = p3_adj
        
        solution = odeint(self._derivatives, state0, t, args=(meal_carbs_g, carb_absorption_rate, exercise_val, sglt2_val))
        
        self.p3 = orig_p3
        
        glucose_trajectory = solution[:, 0].clip(50.0, 450.0)
        insulin_action = solution[:, 1]
        insulin_plasma = solution[:, 2]
        
        return {
            "time_minutes": t,
            "glucose_mgdl": glucose_trajectory,
            "insulin_action": insulin_action,
            "insulin_mU_L": insulin_plasma,
            "peak_glucose": float(np.max(glucose_trajectory)),
            "time_to_peak_min": float(t[np.argmax(glucose_trajectory)]),
            "time_in_range_pct": float(np.mean((glucose_trajectory >= 70) & (glucose_trajectory <= 180)) * 100)
        }

class WindkesselHemodynamicModel:
    """
    2-Element Windkessel Arterial Model for Continuous Blood Pressure & Arterial Stiffness.
    P(t): Arterial Pressure (mmHg)
    R: Peripheral Resistance (mmHg * s / mL)
    C: Arterial Compliance (mL / mmHg)
    """
    def __init__(self, baseline_sbp=138.0, baseline_dbp=86.0):
        self.baseline_sbp = baseline_sbp
        self.baseline_dbp = baseline_dbp

    def simulate_24h_cycle(self, nocturnal_dipping_impaired=True, arb_titrated=False, aerobic_activity_hrs=0.5):
        """
        Simulates 24-hour ambulatory blood pressure profile (1440 minutes).
        In Indian metabolic syndrome, 'non-dipper' status is a major CAD risk factor.
        """
        minutes = np.linspace(0, 24 * 60, 288) # 5-min intervals
        hours = minutes / 60.0
        
        # Circadian baseline
        # Normal profile: dips 10-20% between 23:00 and 06:00
        dip_depth = 4.0 if nocturnal_dipping_impaired else 14.0
        if arb_titrated:
            dip_depth += 6.0  # ARB (Telmisartan) restores circadian dipping
            
        sbp_reduction = 12.0 if arb_titrated else 0.0
        exercise_reduction = 4.5 * (aerobic_activity_hrs / 0.5)
        
        # Circadian wave
        circadian_effect = -dip_depth * np.exp(-((hours - 3.5) / 2.8)**2)
        daytime_elevation = 6.0 * np.sin(np.pi * (hours - 8.0) / 14.0).clip(0, None)
        
        sbp_curve = (self.baseline_sbp - sbp_reduction - exercise_reduction + circadian_effect + daytime_elevation + np.random.normal(0, 2.0, len(hours))).clip(90, 210)
        dbp_curve = (sbp_curve * 0.63 + np.random.normal(0, 1.5, len(hours))).clip(55, 120)
        
        # Dipping ratio = (Day SBP - Night SBP) / Day SBP
        day_sbp = np.mean(sbp_curve[(hours >= 9) & (hours <= 21)])
        night_sbp = np.mean(sbp_curve[(hours >= 0) & (hours <= 6)])
        dipping_ratio_pct = ((day_sbp - night_sbp) / day_sbp) * 100.0
        
        is_dipper = dipping_ratio_pct >= 10.0
        
        return {
            "hours": hours,
            "systolic_bp": sbp_curve,
            "diastolic_bp": dbp_curve,
            "mean_day_sbp": float(day_sbp),
            "mean_night_sbp": float(night_sbp),
            "dipping_ratio_pct": float(dipping_ratio_pct),
            "dipper_status": "Normal Dipper (>10%)" if is_dipper else "High-Risk Non-Dipper (<10%)"
        }
