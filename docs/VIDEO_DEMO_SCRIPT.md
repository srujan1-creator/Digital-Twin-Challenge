# 🎬 CardioTwin-India: 15–20 Minute Official Demo Video Script & Walkthrough

> **Submission for:** Happiest Health – Digital Twin Challenge 2026  
> **Event:** Reimagining & Reforming Healthcare in India Summit 2026  
> **Team Lead:** Kandanala Kota Mohith Srujan (`kandanalasrujan@gmail.com`)  
> **Repository:** https://github.com/srujan1-creator/Digital-Twin-Challenge  
> **Video Target Duration:** 15 – 20 Minutes (Uploaded as **Unlisted YouTube Video**)

---

## 📹 Quick Recording & Upload Checklist

1. **Tooling:** Use [OBS Studio](https://obsproject.com/) (Free) or [Loom](https://www.loom.com/) at 1080p 60fps.
2. **Terminal Setup:**
   ```bash
   # Terminal 1: Run Streamlit Dashboard
   streamlit run app/app.py
   
   # Terminal 2: Run FastAPI Microservice (Optional for API demo)
   uvicorn api.server:app --port 8000
   ```
3. **Browser:** Open `http://localhost:8501` in Fullscreen (`F11`).
4. **YouTube Upload:** Set video visibility to **Unlisted** (accessible to judges without login) and paste the URL into `README.md`.

---

## ⏱️ Video Timeline & Spoken Script

### Segment 1: Introduction, Problem Statement & Indian Context (00:00 – 02:30)
* **Screen Display:** Slide 1 & 2 of `presentation/CardioTwin_India_Happiest_Health_Summit_2026.pdf`
* **Speaker Dialogue:**
  > *"Hello esteemed members of the Happiest Health jury, technical panelists, and clinical experts. My name is Kandanala Kota Mohith Srujan, and today I am proud to present **CardioTwin-India: A Multimodal Physiomarker Digital Twin for Predictive Cardio-Metabolic & Type 2 Diabetes Management**.*
  >
  > *India is currently confronting an unprecedented healthcare emergency. According to the landmark ICMR-INDIAB study, over 101 million Indians live with diabetes, and another 315 million suffer from hypertension. What makes the Indian population uniquely vulnerable is the **Asian Indian Phenotype**—our population develops Type 2 Diabetes and premature cardiovascular disease 10 to 15 years earlier than Western cohorts, characterized by higher visceral adiposity, severe insulin resistance, and early beta-cell exhaustion, even at lower BMIs.*
  >
  > *Standard episodic clinical visits every 3 to 6 months completely miss what happens between visits: silent postprandial glucose excursions, high glycemic variability, and nocturnal non-dipping blood pressure. Our mission in the Happiest Health Digital Twin Challenge 2026 is to bridge static EHR records with high-frequency wearable sensor streams to construct a dynamic, personalized virtual patient twin."*

---

### Segment 2: Multi-Scale System Architecture & Digital Twin Theory (02:30 – 05:00)
* **Screen Display:** `docs/architecture/architecture_diagram.png`
* **Speaker Dialogue:**
  > *"Let us examine the architecture of CardioTwin-India. Unlike black-box models, CardioTwin is biophysically grounded.*
  >
  > *In Layer 1, we ingest dual data streams: static longitudinal EHR—such as baseline HbA1c, lipid profiles (specifically atherogenic dyslipidemia with high triglycerides and low HDL), and renal biomarkers like eGFR and UACR—coupled with continuous 5-minute wearable telemetry: Continuous Glucose Monitoring (CGM), PPG photoplethysmography heart rate, heart rate variability (RMSSD), and continuous blood pressure.*
  >
  > *In Layer 2, our temporal fusion pipeline filters sensor artifacts and normalizes circadian rhythms.*
  >
  > *In Layer 3, at the heart of our twin, we couple two deterministic biophysical systems: the **Bergman Minimal Model of Glucose-Insulin Dynamics** implemented as non-linear ordinary differential equations (ODEs), and a **2-Element Windkessel Cardiovascular Hemodynamics Model**. On top of this physiological core, we integrate multi-horizon machine learning: an autoregressive sequence model for short-term 120-minute forward trajectories, and gradient boosted ensembles (XGBoost) for long-term 10-year ASCVD risk and Diabetic Kidney Disease progression.*
  >
  > *In Layer 4, we deliver clinical decision support through an interactive Streamlit portal, counterfactual 'what-if' simulation, explainable clinical guidelines, and standard HL7 FHIR R4 export ready for Ayushman Bharat Digital Mission (ABDM)."*

---

### Segment 3: Live Application Walkthrough & Real-Time Telemetry (05:00 – 08:30)
* **Screen Display:** Streamlit Application (`http://localhost:8501`) -> Tab: `📊 Live Digital Twin & Telemetry`
* **Speaker Dialogue:**
  > *(Switch to Streamlit UI)*
  > *"Here is the live CardioTwin-India application. At the top, we see our active virtual patient profile. Let us examine **Ramesh V. Sharma**, a 54-year-old male from Bengaluru with a 7.5-year history of Type 2 Diabetes, baseline HbA1c of 8.6%, and clinic blood pressure of 148/92 mmHg.*
  >
  > *Looking at the live telemetry dashboard, we see continuous 72-hour streaming sensor data. The top plot displays the CGM glucose trajectory. Notice the target glycemic band highlighted in green between 70 and 180 mg/dL. Ramesh's Time-in-Range (TIR) is currently only 58.2%, well below the clinical target of 70%. We clearly see postprandial surges after breakfast, lunch, and dinner exceeding 260 mg/dL.*
  >
  > *The middle chart displays continuous ambulatory blood pressure. Notice that during the nighttime hours between 11 PM and 6 AM, Ramesh's systolic blood pressure fails to dip by more than 10%. He exhibits a high-risk 'non-dipper' circadian profile, which according to clinical literature increases cardiovascular mortality and stroke risk by 2.4-fold.*
  >
  > *The bottom chart plots PPG pulse and autonomic tone via HRV RMSSD, showing depressed parasympathetic recovery during episodes of acute glucotoxicity."*

---

### Segment 4: Organ-Level Virtual Dynamics & Multi-Scale Strain (08:30 – 11:30)
* **Screen Display:** Streamlit Navigation -> `🫀 Organ-Level Virtual Dynamics`
* **Speaker Dialogue:**
  > *"Now let us navigate to the Organ-Level Virtual Dynamics module. A true Digital Twin must reflect organ compartment strain.*
  >
  > *Here, CardioTwin computes a 5-axis physiological radar: Pancreatic Strain, Arterial Stiffness, Myocardial Workload, Glomerular Stress, and Hepatic Insulin Resistance.*
  >
  > *We observe that Ramesh's pancreatic beta-cell reserve is depleted down to 38.5% due to chronic glucotoxicity. His arterial stiffness score is elevated at 72/100, driven by a wide pulse pressure. His renal glomerular strain is critical, indicating hyperfiltration and endothelial shear stress. This organ-level awareness allows clinicians to treat systemic cardio-renal-metabolic dysfunction holistically rather than treating isolated blood test numbers."*

---

### Segment 5: Counterfactual In-Silico 'What-If' Clinical Simulator (11:30 – 15:00)
* **Screen Display:** Streamlit Navigation -> `🧪 Counterfactual 'What-If' Simulator`
* **Speaker Dialogue:**
  > *(Highlight sliders on screen)*
  > *"Now we arrive at the most transformative capability of CardioTwin: the **Counterfactual 'What-If' Clinical Simulator**. Before changing a prescription or issuing lifestyle advice, the physician can simulate interventions in-silico.*
  >
  > *Let us simulate a realistic, patient-acceptable regimen:*
  > *1. In Nutritional Intervention: Ramesh typically consumes high-glycemic white rice. Let us dial in a **25% reduction in refined carbohydrates** by substituting half his meal with whole millets and lentils.*
  > *2. In Lifestyle: Let us prescribe a **20-minute brisk walk** immediately after dinner.*
  > *3. In Pharmacotherapy: Let us activate **SGLT2 inhibitor titration (Empagliflozin 10mg)** and move his **Telmisartan ARB to bedtime for chronotherapy**.*
  >
  > *(Click/observe instant recalculation)*
  > *Observe the in-silico outcomes instantly recomputed by the Bergman and Windkessel ODE solvers:*
  > *• Peak postprandial glucose is dramatically blunted from 265 mg/dL down to 184 mg/dL—a 81 mg/dL reduction!*
  > *• Time-in-Range (TIR) improves by +26.4%, reaching the recommended 75% target.*
  > *• Most importantly, bedtime Telmisartan chronotherapy restores Ramesh's nocturnal blood pressure dipping from an abnormal 4.2% up to 13.8%, successfully reclassifying him as a 'Normal Dipper' and mitigating acute stroke risk!*
  >
  > *This demonstrates how a Digital Twin provides objective, patient-specific proof of concept for clinical interventions."*

---

### Segment 6: Multi-Horizon AI Predictive Engine & Risk Horizons (15:00 – 17:30)
* **Screen Display:** Streamlit Navigation -> `🔮 Multi-Horizon AI Predictive Engine`
* **Speaker Dialogue:**
  > *"Next, let us explore our multi-horizon AI predictive engine.*
  >
  > *In the Short-Term Horizon (Next 120 Minutes), our autoregressive sequence model projects real-time trajectories with 95% physiological confidence bands. If a patient logs an impending high-carbohydrate snack, the model predicts whether an acute spike or nocturnal hypoglycemia will occur, triggering immediate preventive alerts.*
  >
  > *In the Medium-Term Horizon (90 Days), we predict glycemic decompensation risk and HbA1c trajectory, comparing the unmanaged drift against the digital twin-guided plan.*
  >
  > *In the Long-Term Horizon (10 Years), our machine learning models calculate the 10-Year ASCVD Cardiovascular Risk score using the Modified Framingham algorithm calibrated with the 1.5x South Asian multiplier recommended by ACC/AHA guidelines. We see that Ramesh has a 24.8% 10-year cardiovascular risk. Our SHAP feature importance identifies age, LDL cholesterol, systolic blood pressure, and HbA1c as the primary drivers. Simultaneously, our Random Forest classifier stages his Diabetic Kidney Disease (DKD) as Stage 2 with microalbuminuria."*

---

### Segment 7: Clinical Guidelines & HL7 FHIR R4 Interoperability (17:30 – 19:15)
* **Screen Display:** Streamlit Navigation -> `🩺 Clinical Insights` followed by `🏥 FHIR R4 Interoperability`
* **Speaker Dialogue:**
  > *"In our Clinical Insights module, CardioTwin maps every finding against national guidelines: the ICMR-INDIAB consensus and RSSDI 2026 guidelines. It specifically warns that Ramesh's Triglyceride-to-HDL ratio of 6.8 signifies atherogenic dyslipidemia and small dense LDL particles, warranting Statin titration.*
  >
  > *Furthermore, interoperability is fundamental to healthcare adoption. In our FHIR R4 module, CardioTwin automatically serializes all patient demographics, clinical lab observations, vital sign panels, and risk assessments into valid **HL7 FHIR R4 JSON bundles**.*
  >
  > *These bundles are 100% compliant with India's **Ayushman Bharat Digital Mission (ABDM)** standards, enabling seamless synchronization with the national ABHA health locker and hospital electronic health record systems."*

---

### Segment 8: Conclusion & Summit Impact (19:15 – 20:00)
* **Screen Display:** Slide 12 of Presentation & GitHub Repository page
* **Speaker Dialogue:**
  > *"In conclusion, CardioTwin-India proves that combining biophysical ODE modeling with machine learning and wearable telemetry can transform chronic disease care in India from reactive crisis management into proactive, individualized precision care.*
  >
  > *All code, synthetic datasets calibrated to ICMR-INDIAB, machine learning models, architecture blueprints in PDF and PPTX, presentation decks, and unit tests are fully documented and publicly available under the open-source MIT License in our GitHub repository.*
  >
  > *Thank you Happiest Health for organizing this inspiring challenge. I look forward to presenting CardioTwin-India at the Reimagining & Reforming Healthcare in India Summit 2026 in Bengaluru!"*
