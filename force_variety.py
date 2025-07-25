#!/usr/bin/env python3
"""
Generate predictions that should create more variety in metrics
"""

import requests
import json

# Try different customer profiles to get variety
test_customers = [
    # Profile 1: Try to trigger high churn probability
    {
        "gender": "Female",
        "SeniorCitizen": 1,
        "Partner": "No", 
        "Dependents": "No",
        "tenure": 1,  # Very new customer
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No", 
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 120.0,  # Very high charges
        "TotalCharges": 120.0     # New customer, high charges
    },
    # Profile 2: Another high-risk attempt
    {
        "gender": "Male",
        "SeniorCitizen": 1,
        "Partner": "No",
        "Dependents": "No", 
        "tenure": 2,
        "PhoneService": "Yes",
        "MultipleLines": "Yes",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No", 
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 110.0,
        "TotalCharges": 220.0
    },
    # Profile 3: Extreme high-risk
    {
        "gender": "Female",
        "SeniorCitizen": 1,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "Yes", 
        "MultipleLines": "Yes",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes", 
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 150.0,  # Extremely high
        "TotalCharges": 150.0
    }
]

def make_prediction(customer, profile_name):
    try:
        response = requests.post("http://localhost:8000/predict", json=customer)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {profile_name}")
            print(f"   Prediction: {result['churn_prediction']} | Risk: {result['risk_level']} | Probability: {result['churn_probability']:.4f}")
            return result
        else:
            print(f"❌ {profile_name} failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ {profile_name} error: {e}")
        return None

if __name__ == "__main__":
    print("🎯 Trying to generate diverse predictions...")
    print("=" * 60)
    
    for i, customer in enumerate(test_customers, 1):
        make_prediction(customer, f"High-risk Profile {i}")
        print()
    
    print("📊 Now check Prometheus with these queries:")
    print("   churn_predictions_total")
    print("   sum(churn_predictions_total)")
    print("   churn_predictions_total{risk_level=\"High\"}")
    print("   churn_predictions_total{prediction=\"Yes\"}")