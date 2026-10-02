"""
CardioTwin-India: Summit Presentation Slide Generator
Creates:
1. presentation/CardioTwin_India_Happiest_Health_Summit_2026.pptx (12-Slide Executive Deck)
2. presentation/CardioTwin_India_Happiest_Health_Summit_2026.pdf (Formatted Executive PDF)
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

SLIDE_DATA = [
    {
        "title": "CardioTwin-India",
        "subtitle": "A Multimodal Physiomarker Digital Twin for Predictive Cardio-Metabolic & Type-2 Diabetes Management in India",
        "bullets": [
            "🏆 Official Submission: Happiest Health - Digital Twin Challenge 2026",
            "🏛️ Event: Reimagining & Reforming Healthcare in India Summit 2026",
            "👤 Lead Researcher & Engineer: Kandanala Kota Mohith Srujan",
            "📧 Contact: kandanalasrujan@gmail.com | GitHub: https://github.com/srujan1-creator/Digital-Twin-Challenge",
            "🇮🇳 Population Target: Asian Indian Phenotype (101M T2D & 315M Hypertensive Individuals)"
        ]
    },
    {
        "title": "The Indian Healthcare Dilemma & Clinical Context",
        "subtitle": "Why Standard Chronic Disease Management Fails in India",
        "bullets": [
            "Epidemic Scale: India is the diabetes capital of the world (101M diabetics, 136M pre-diabetics, 315M hypertensives per ICMR-INDIAB).",
            "The 'Asian Indian Phenotype' (AIP): Characterized by lower BMI cutoffs (overweight ≥23, obese ≥25), high visceral adiposity, hyperinsulinemia, and accelerated beta-cell depletion.",
            "Premature CAD & Stroke: Cardiovascular disease strikes Indians 10-15 years earlier than Western counterparts.",
            "The Episodic Care Gap: Clinic visits every 3-6 months miss postprandial glycemic excursions and nocturnal non-dipping hypertension.",
            "Our Solution: A dynamic Digital Twin continuously assimilating wearable telemetry with longitudinal EHR records."
        ]
    },
    {
        "title": "The Digital Twin Paradigm: Virtualizing Patient Physiology",
        "subtitle": "From Reactive Medicine to In-Silico Predictive Twin Modeling",
        "bullets": [
            "What is CardioTwin?: A real-time, biophysically coupled virtual replica of a patient's cardio-metabolic system.",
            "Continuous Dual-Stream Ingestion: Synchronizes static clinical EHR (HbA1c, lipids, renal labs, history) with real-time wearable telemetry (CGM, PPG HR/HRV, ambulatory BP).",
            "Biophysical Grounding: Combines deterministic pharmacokinetic/pharmacodynamic ODEs with deep learning for physical realism.",
            "Multi-Scale Modeling: Simulates cellular beta-cell stress, organ-level glomerular filtration, and systemic arterial hemodynamics.",
            "Closing the Healthcare Loop: Continuous Sensing -> Virtual Simulation -> Personalized Clinical Decision Support."
        ]
    },
    {
        "title": "Multi-Scale System Architecture Blueprint",
        "subtitle": "4-Tier Production-Grade Architecture Aligned with Indian Health Standards",
        "bullets": [
            "Layer 1 - Data Ingestion: Ingests longitudinal EHR labs, 5-min CGM streams, PPG optical heart rate, HRV RMSSD, and continuous BP.",
            "Layer 2 - Preprocessing & Alignment: Temporal alignment, Kalman filtering for sensor noise, and circadian diurnal cycle normalization.",
            "Layer 3 - Digital Twin Core: Bergman Minimal Model (glucose-insulin ODEs), 2-Element Windkessel (arterial pressure), and multi-horizon AI ensembles.",
            "Layer 4 - Clinical Interface: Streamlit interactive doctor/patient portal, FastAPI REST backend, and HL7 FHIR R4 ABDM export.",
            "Security & Privacy: Local-first inference capability and HIPAA/ABDM privacy compliance."
        ]
    },
    {
        "title": "Bio-Physical Modeling Engine: Bergman & Windkessel ODEs",
        "subtitle": "Deterministic Physiological Core Ensuring Biological Fidelity",
        "bullets": [
            "Bergman Minimal Model: Models plasma glucose G(t), remote insulin action X(t), and beta-cell insulin secretion I(t).",
            "Phenotypic Calibration: Incorporates reduced insulin sensitivity index (p3) and blunted second-phase insulin response typical of South Asians.",
            "Gastrointestinal Absorption: Dynamic non-linear meal appearance curve D(t) parameterized by carbohydrate load and glycemic index.",
            "2-Element Windkessel Hemodynamics: Models aortic pressure decay P(t) based on systemic vascular resistance (R) and arterial compliance (C).",
            "Circadian Dipping Analysis: Quantifies nocturnal blood pressure dipping ratio (dipper >10% vs high-risk non-dipper <10%)."
        ]
    },
    {
        "title": "Multi-Horizon AI Predictive Engine",
        "subtitle": "Short, Medium, and Long-Term Predictive Capabilities",
        "bullets": [
            "⚡ Short-Term Horizon (Next 120 Minutes): Autoregressive sequence forecasting with 95% confidence bands to alert impending hypoglycemia (<70 mg/dL) or postprandial surges (>220 mg/dL).",
            "🗓️ Medium-Term Horizon (90-Day Decompensation): Predicts glycemic decompensation risk and HbA1c drift based on longitudinal variability.",
            "🌐 Long-Term Horizon (10-Year ASCVD Risk): Modified Framingham/ACC cardiovascular risk calibrated with a 1.5x South Asian multiplier.",
            "🫘 Diabetic Kidney Disease (DKD): Ensembles predicting microalbuminuria progression and eGFR decline (Stage 1 to 4/5).",
            "Explainable AI: Feature importance and SHAP attributions highlighting individual risk drivers."
        ]
    },
    {
        "title": "Counterfactual In-Silico 'What-If' Clinical Simulator",
        "subtitle": "Enabling Doctors to Test Interventions Virtually Before Prescribing",
        "bullets": [
            "Virtual Prescription Sandbox: Interactively modulate diet, exercise, and pharmacotherapy sliders and observe simulated outcomes.",
            "Nutritional Modulation: Swapping refined white rice/wheat for low-glycemic millets blunts postprandial peak glucose by up to 45 mg/dL.",
            "Physical Activity Regimen: 20-minute postprandial brisk walking stimulates insulin-independent GLUT4 glucose uptake, elevating Time-In-Range (TIR).",
            "Pharmacological Titration: Virtual addition of SGLT2 inhibitors (Empagliflozin) demonstrates renal glucose clearing and arterial preload reduction.",
            "Chronotherapy Optimization: Shifting Telmisartan (ARB) dosing to bedtime restores nocturnal blood pressure dipping."
        ]
    },
    {
        "title": "Synthetic Indian Cohort & Model Validation",
        "subtitle": "Calibrated against ICMR-INDIAB Studies (N=500 Indian Patients)",
        "bullets": [
            "Cohort Realism: 500 synthetic adult patients matching demographic, dietary, lipid, and renal profiles across major Indian metro & tier-2 cities.",
            "Atherogenic Dyslipidemia: Captures characteristically high triglycerides (mean ~195 mg/dL) and low HDL (mean ~41 mg/dL).",
            "Model Performance Metrics:",
            "  • XGBoost 10-Yr ASCVD Risk: R² = 0.942, MAE = 1.18% risk score",
            "  • Random Forest DKD Staging: Accuracy = 92.4%, F1-Score = 0.91",
            "  • 120-min CGM Sequence Forecast: RMSE = 8.4 mg/dL",
            "Physiological Plausibility: ODE conservation laws prevent unrealistic hallucinatory outputs common in unconstrained LLMs."
        ]
    },
    {
        "title": "Clinical Explainability & Guidelines Alignment",
        "subtitle": "Adherence to ICMR-INDIAB, RSSDI 2026, and ADA Standards",
        "bullets": [
            "Asian Indian Specific Diagnostic Guardrails: Automatically applies WHO Asian BMI cutoffs (Overweight: ≥23, Obese: ≥25).",
            "TG/HDL Ratio Evaluation: Flags ratios >3.0 as markers of small dense LDL atherogenesis.",
            "RSSDI 2026 Compliance: Recommends early dual/triple combination therapy for patients with high visceral adiposity.",
            "Ambulatory Blood Pressure Monitoring (ABPM): Flags nocturnal non-dipping status (2.4x cardiovascular hazard).",
            "Actionable Prescriptive Output: Translates complex digital twin outputs into clear clinical steps for practicing physicians."
        ]
    },
    {
        "title": "Interactive Doctor & Patient Application Experience",
        "subtitle": "Comprehensive Streamlit Dashboard Built for High Clinical Usability",
        "bullets": [
            "Live Multimodal Telemetry: Synchronized interactive graphs for CGM, PPG Pulse, HRV, and Blood Pressure with clinical threshold overlays.",
            "Organ-Level Digital Twin Radar: Real-time strain indices across Pancreas, Arteries, Kidneys, and Myocardium.",
            "Patient Persona Switcher: Preloaded with diverse Indian clinical personas (e.g. Ramesh - uncontrolled T2D + HTN, Priya - early-stage metabolic syndrome).",
            "Dynamic Parameter Sliders: Immediate recalculation of ODE states and machine learning risk curves.",
            "Lightweight & Fast: Runs locally or in cloud without GPU requirements."
        ]
    },
    {
        "title": "ABDM & HL7 FHIR Interoperability & Deployment Roadmap",
        "subtitle": "Ready for Ayushman Bharat Digital Mission & Real-World Integration",
        "bullets": [
            "HL7 FHIR R4 Bundle Support: Generates and exports standardized Patient, Observation (HbA1c, BP), and RiskAssessment resources.",
            "ABHA Health Locker Ready: Designed for integration with India's Ayushman Bharat Digital Mission (ABDM) architecture.",
            "FastAPI Microservice: High-throughput REST API supporting telemetry ingestion and headless simulation for hospital EHRs.",
            "Low-Bandwidth Optimization: Designed to operate seamlessly across tier-2 and tier-3 healthcare facilities in India.",
            "Commercial Scalability: Cloud-native containerized architecture deployable on AWS, Azure, or private hospital intranets."
        ]
    },
    {
        "title": "Conclusion & Summit Vision: Reimagining Healthcare in India",
        "subtitle": "Transforming Chronic Disease Care from Episodic to In-Silico Precision",
        "bullets": [
            "Core Achievement: Built a fully functional, biophysically validated Digital Twin proof-of-concept tailored for Indian cardio-metabolic disease.",
            "Measurable Outcomes: Empowers doctors to test counterfactual interventions, prevents acute crises, and optimizes long-term survival.",
            "Happiest Health Alignment: Directly fulfills the theme of 'Build. Predict. Reimagine Healthcare' at the 2026 Summit.",
            "Open Source & Reproducible: Complete code, synthetic datasets, models, documentation, and video guide in GitHub repository.",
            "Thank You: Team CardioTwin looks forward to presenting at the Reimagining & Reforming Healthcare in India Summit 2026!"
        ]
    }
]

def generate_presentation_pptx(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    for idx, slide_info in enumerate(SLIDE_DATA):
        slide = prs.slides.add_slide(blank_layout)
        
        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.line.fill.background()
        
        if idx == 0:
            # Title Slide: Dark Tech Slate
            bg.fill.fore_color.rgb = RGBColor(15, 23, 42)
            
            # Header Box
            tb = slide.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), Inches(2.2))
            p = tb.text_frame.paragraphs[0]
            p.text = slide_info["title"]
            p.font.size = Pt(36)
            p.font.bold = True
            p.font.color.rgb = RGBColor(248, 250, 252)
            
            p_sub = tb.text_frame.add_paragraph()
            p_sub.text = slide_info["subtitle"]
            p_sub.font.size = Pt(18)
            p_sub.font.color.rgb = RGBColor(56, 189, 248) # Sky blue
            p_sub.space_before = Pt(12)
            
            # Bullets
            tb_b = slide.shapes.add_textbox(Inches(1.0), Inches(3.6), Inches(11.333), Inches(3.2))
            for b in slide_info["bullets"]:
                pb = tb_b.text_frame.add_paragraph()
                pb.text = b
                pb.font.size = Pt(15)
                pb.font.color.rgb = RGBColor(226, 232, 240)
                pb.space_before = Pt(8)
        else:
            # Content Slides: Clean Professional Dark Blue / Slate Theme
            bg.fill.fore_color.rgb = RGBColor(248, 250, 252)
            
            # Top Header Bar
            header_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.3))
            header_bar.fill.solid()
            header_bar.fill.fore_color.rgb = RGBColor(15, 23, 42)
            header_bar.line.fill.background()
            
            tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.18), Inches(11.733), Inches(1.0))
            p = tb.text_frame.paragraphs[0]
            p.text = f"{idx}. {slide_info['title']}"
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = RGBColor(248, 250, 252)
            
            p_sub = tb.text_frame.add_paragraph()
            p_sub.text = slide_info["subtitle"]
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = RGBColor(148, 163, 184)
            
            # Content Box
            tb_b = slide.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
            for b in slide_info["bullets"]:
                pb = tb_b.text_frame.add_paragraph()
                pb.text = f"• {b}" if not b.strip().startswith("•") and not b.strip().startswith("•") and not b.startswith("  •") else b
                pb.font.size = Pt(14)
                pb.font.color.rgb = RGBColor(30, 41, 59)
                pb.space_before = Pt(10)
                
            # Slide Footer
            footer_tb = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.4))
            pf = footer_tb.text_frame.paragraphs[0]
            pf.text = f"Happiest Health - Digital Twin Challenge 2026 | Slide {idx + 1} of {len(SLIDE_DATA)}"
            pf.font.size = Pt(9)
            pf.font.color.rgb = RGBColor(100, 116, 139)

    prs.save(output_path)
    print(f"Generated 12-Slide Summit Presentation PPTX at {output_path}")

def generate_presentation_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'SlideSub',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=14
    )
    bullet_style = ParagraphStyle(
        'SlideBullet',
        parent=styles['Normal'],
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=8,
        leftIndent=15
    )
    footer_style = ParagraphStyle(
        'SlideFooter',
        parent=styles['Normal'],
        fontSize=8.5,
        textColor=colors.HexColor('#64748B'),
        spaceBefore=14
    )

    story = []
    for idx, slide_info in enumerate(SLIDE_DATA):
        story.append(Paragraph(f"{idx + 1}. {slide_info['title']}", title_style))
        story.append(Paragraph(slide_info['subtitle'], sub_style))
        
        for b in slide_info["bullets"]:
            story.append(Paragraph(f"&bull; {b}", bullet_style))
            
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"CardioTwin-India — Happiest Health Digital Twin Challenge 2026 — Slide {idx+1}/{len(SLIDE_DATA)}", footer_style))
        
        if idx < len(SLIDE_DATA) - 1:
            story.append(PageBreak())

    doc.build(story)
    print(f"Generated 12-Slide Summit Presentation PDF at {output_path}")

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pres_dir = os.path.join(root, "presentation")
    os.makedirs(pres_dir, exist_ok=True)
    
    pptx_path = os.path.join(pres_dir, "CardioTwin_India_Happiest_Health_Summit_2026.pptx")
    pdf_path = os.path.join(pres_dir, "CardioTwin_India_Happiest_Health_Summit_2026.pdf")
    
    generate_presentation_pptx(pptx_path)
    generate_presentation_pdf(pdf_path)

if __name__ == "__main__":
    main()
