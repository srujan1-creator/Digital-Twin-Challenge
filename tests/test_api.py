"""
CardioTwin-India: API Endpoint Tests
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from api.server import app

class TestCardioTwinAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["models_loaded"])

    def test_list_patients(self):
        response = self.client.get("/api/patients")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]["patient_id"], "IND-PT-1001")

    def test_what_if_simulation_endpoint(self):
        payload = {
            "patient_id": "IND-PT-1001",
            "carb_intake_reduction_pct": 25.0,
            "postprandial_exercise_mins": 20,
            "titrate_sglt2i": True,
            "titrate_telmisartan": True,
            "simulation_horizon_hours": 3
        }
        response = self.client.post("/api/simulate/what-if", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("glucose", data)
        self.assertIn("blood_pressure", data)
        self.assertGreater(data["glucose"]["intervention"]["peak_glucose_reduction"], 0)

    def test_fhir_export_endpoint(self):
        response = self.client.get("/api/fhir/patient/IND-PT-1001")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["resourceType"], "Bundle")
        self.assertEqual(len(data["entry"]), 4)

if __name__ == "__main__":
    unittest.main()
