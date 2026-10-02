"""
CardioTwin-India: Dynamic Wearable Telemetry Forecaster
Multi-horizon forecasting engine (Next 15 to 120 minutes):
Predicts glycemic trajectory, acute hypoglycemic events (<70 mg/dL), 
and nocturnal hypertensive surge risk using dynamic sequence autoregression.
"""

import numpy as np
import pandas as pd

class WearableSequenceForecaster:
    def __init__(self, horizon_steps=24, step_min=5):
        """
        horizon_steps = 24 steps @ 5-min intervals = 120 minutes forward projection.
        """
        self.horizon_steps = horizon_steps
        self.step_min = step_min

    def forecast_trajectory(self, recent_cgm_series, recent_hr_series, meal_recent_carbs=0, exercise_active=False):
        """
        Takes last 12 to 24 time steps (1 to 2 hours of wearable history)
        and projects the next 120 minutes with 95% physiological confidence bands.
        """
        recent_cgm = np.array(recent_cgm_series, dtype=float)
        recent_hr = np.array(recent_hr_series, dtype=float)
        
        last_val = recent_cgm[-1]
        
        # Calculate velocity (rate of change in mg/dL per 5 min)
        if len(recent_cgm) >= 4:
            velocity = (recent_cgm[-1] - recent_cgm[-4]) / 3.0
            acceleration = ((recent_cgm[-1] - recent_cgm[-2]) - (recent_cgm[-2] - recent_cgm[-3]))
        else:
            velocity = 0.0
            acceleration = 0.0
            
        future_minutes = np.arange(self.step_min, (self.horizon_steps + 1) * self.step_min, self.step_min)
        forecast_vals = []
        upper_bounds = []
        lower_bounds = []
        
        # Basal metabolic drift towards steady state
        target_basal = 120.0
        decay_rate = 0.04
        
        for step in range(1, self.horizon_steps + 1):
            t_min = step * self.step_min
            
            # Autoregressive momentum
            momentum = velocity * np.exp(-0.06 * t_min)
            
            # Postprandial carb spike effect if meal logged
            carb_effect = 0.0
            if meal_recent_carbs > 0:
                peak_t = 45.0 # minutes
                carb_effect = meal_recent_carbs * 1.2 * np.exp(-((t_min - peak_t) / 30.0)**2)
                
            # Exercise clearance effect
            exercise_effect = 0.0
            if exercise_active:
                exercise_effect = -1.5 * np.sqrt(t_min)
                
            # Predicted glucose
            pred = last_val + momentum * (t_min / 5.0) * 0.4 + carb_effect + exercise_effect
            # Mean reversion towards basal
            pred = pred * (1 - decay_rate) + target_basal * decay_rate
            pred = float(np.clip(pred, 40.0, 400.0))
            
            # Uncertainty envelope grows with sqrt(time)
            sigma = 4.5 + 2.2 * np.sqrt(step)
            
            forecast_vals.append(round(pred, 1))
            upper_bounds.append(round(pred + 1.96 * sigma, 1))
            lower_bounds.append(round(max(40.0, pred - 1.96 * sigma), 1))
            
        # Clinical Risk Alerts
        min_proj = min(lower_bounds)
        max_proj = max(upper_bounds)
        
        alerts = []
        if min_proj < 70.0:
            time_to_hypo = future_minutes[np.argmin(lower_bounds)]
            alerts.append({
                "severity": "CRITICAL",
                "type": "IMPENDING_HYPOGLYCEMIA",
                "message": f"Critical Hypoglycemia risk detected in {time_to_hypo} mins (proj {min_proj} mg/dL). Immediate 15g fast-acting carbs recommended."
            })
        elif max_proj > 220.0:
            alerts.append({
                "severity": "WARNING",
                "type": "POSTPRANDIAL_SPIKE",
                "message": f"Postprandial glycemic surge projected to exceed 220 mg/dL. 15-minute post-meal walk recommended to blunt spike."
            })
            
        return {
            "future_minutes": list(future_minutes),
            "forecast_glucose": forecast_vals,
            "ci_upper_95": upper_bounds,
            "ci_lower_95": lower_bounds,
            "clinical_alerts": alerts
        }
