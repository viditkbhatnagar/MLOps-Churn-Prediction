# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_predict_valid():
    customer_data = {
        "gender": "Male",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 12,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 70.35,
        "TotalCharges": 844.20
    }
    
    response = client.post("/predict", json=customer_data)
    
    # Check if model is loaded
    if response.status_code == 503:
        pytest.skip("Model not loaded")
    
    assert response.status_code == 200
    data = response.json()
    assert "churn_probability" in data
    assert "churn_prediction" in data
    assert "risk_level" in data

def test_predict_invalid():
    invalid_data = {
        "gender": "Invalid",
        "SeniorCitizen": 2,  # Invalid value
        "tenure": -1  # Invalid value
    }
    
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_batch_predict():
    batch_data = {
        "customers": [
            {
                "gender": "Female",
                "SeniorCitizen": 1,
                "Partner": "No",
                "Dependents": "Yes",
                "tenure": 24,
                "PhoneService": "Yes",
                "MultipleLines": "Yes",
                "InternetService": "DSL",
                "OnlineSecurity": "Yes",
                "OnlineBackup": "No",
                "DeviceProtection": "Yes",
                "TechSupport": "Yes",
                "StreamingTV": "Yes",
                "StreamingMovies": "Yes",
                "Contract": "Two year",
                "PaperlessBilling": "No",
                "PaymentMethod": "Bank transfer",
                "MonthlyCharges": 85.50,
                "TotalCharges": 2050.00
            }
        ]
    }
    
    response = client.post("/batch_predict", json=batch_data)
    
    if response.status_code == 503:
        pytest.skip("Model not loaded")
    
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert "total_processed" in data
    assert data["total_processed"] == 1