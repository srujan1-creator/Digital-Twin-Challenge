"""
CardioTwin-India: FHIR R4 Interoperability & Export Component
Compliant with Ayushman Bharat Digital Mission (ABDM) / HL7 FHIR R4 standards.
"""

import json
import streamlit as st

def render_fhir_export(patient):
    st.markdown("### 🏥 Health Interoperability & FHIR R4 Bundle")
    st.caption("Standardized clinical data exchange compliant with HL7 FHIR R4 and Ayushman Bharat Digital Mission (ABDM) protocols.")
    
    sbp_val = int(patient["bp"].split("/")[0])
    dbp_val = int(patient["bp"].split("/")[1].replace(" mmHg", ""))
    
    fhir_bundle = {
        "resourceType": "Bundle",
        "id": f"cardiotwin-bundle-{patient['patient_id'].lower()}",
        "type": "collection",
        "timestamp": "2026-10-02T10:00:00Z",
        "entry": [
            {
                "fullUrl": f"urn:uuid:patient-{patient['patient_id']}",
                "resource": {
                    "resourceType": "Patient",
                    "id": patient["patient_id"],
                    "identifier": [
                        {
                            "system": "https://healthid.ndhm.gov.in",
                            "value": f"ABHA-91-{patient['patient_id']}"
                        }
                    ],
                    "name": [{"use": "official", "text": patient["name"]}],
                    "gender": patient["gender"].lower(),
                    "address": [{"city": patient["city"], "country": "IND"}],
                    "extension": [
                        {
                            "url": "http://happiesthealth.org/fhir/StructureDefinition/digital-twin-phenotype",
                            "valueString": patient["phenotype"]
                        }
                    ]
                }
            },
            {
                "fullUrl": f"urn:uuid:obs-hba1c-{patient['patient_id']}",
                "resource": {
                    "resourceType": "Observation",
                    "id": f"obs-hba1c-{patient['patient_id']}",
                    "status": "final",
                    "category": [
                        {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory"}]}
                    ],
                    "code": {
                        "coding": [{"system": "http://loinc.org", "code": "4548-4", "display": "Hemoglobin A1c/Hemoglobin.total in Blood"}]
                    },
                    "subject": {"reference": f"Patient/{patient['patient_id']}"},
                    "valueQuantity": {"value": patient["hba1c"], "unit": "%", "system": "http://unitsofmeasure.org", "code": "%"}
                }
            },
            {
                "fullUrl": f"urn:uuid:obs-bp-{patient['patient_id']}",
                "resource": {
                    "resourceType": "Observation",
                    "id": f"obs-bp-{patient['patient_id']}",
                    "status": "final",
                    "category": [
                        {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}]}
                    ],
                    "code": {
                        "coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel with all children optional"}]
                    },
                    "subject": {"reference": f"Patient/{patient['patient_id']}"},
                    "component": [
                        {
                            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]},
                            "valueQuantity": {"value": sbp_val, "unit": "mmHg"}
                        },
                        {
                            "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"}]},
                            "valueQuantity": {"value": dbp_val, "unit": "mmHg"}
                        }
                    ]
                }
            },
            {
                "fullUrl": f"urn:uuid:risk-ascvd-{patient['patient_id']}",
                "resource": {
                    "resourceType": "RiskAssessment",
                    "id": f"risk-ascvd-{patient['patient_id']}",
                    "status": "final",
                    "subject": {"reference": f"Patient/{patient['patient_id']}"},
                    "method": {
                        "coding": [{"system": "http://happiesthealth.org/fhir/risk-assessment-methods", "code": "CardioTwin-India-AI", "display": "Modified Framingham with South Asian Multiplier"}]
                    },
                    "prediction": [
                        {
                            "outcome": {"text": "10-Year ASCVD Cardiovascular Event Risk"},
                            "probabilityDecimal": patient["ascvd_10yr"] / 100.0,
                            "qualitativeRisk": {"text": "High Risk (>20%)" if patient["ascvd_10yr"] >= 20 else "Moderate Risk"}
                        }
                    ]
                }
            }
        ]
    }
    
    json_str = json.dumps(fhir_bundle, indent=2)
    
    st.download_button(
        label="📥 Download HL7 FHIR R4 Patient Bundle (JSON)",
        data=json_str,
        file_name=f"FHIR_CardioTwin_{patient['patient_id']}.json",
        mime="application/json"
    )
    
    st.markdown("##### FHIR Resource JSON Preview")
    st.json(fhir_bundle, expanded=False)
