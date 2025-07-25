#!/usr/bin/env python3
"""
Generate diverse customer predictions to show different risk levels
"""

import requests
import json
import time

# High-risk customer profile (more likely to churn)
high_risk_customers = [
    {
        "gender": "Male",
        "SeniorCitizen": 1,
        "Partner": "No",
        "Dependents": "No", 
        "tenure": 1,  # Very low tenure
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes",
        "Contract": "Month-to-month",  # Short-term contract
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",  # Higher churn risk
        "MonthlyCharges": 95.0,  # High charges
        "TotalCharges": 95.0   # Low total (new customer)
    },
    {
        "gender": "Female", 
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 3,
        "PhoneService": "Yes",
        "MultipleLines": "No", 
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 85.0,
        "TotalCharges": 255.0
    }
]

def make_prediction(customer, label):
    try:
        response = requests.post("http://localhost:8000/predict", json=customer)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {label}: {result['churn_prediction']} (Risk: {result['risk_level']}, Prob: {result['churn_probability']:.3f})")
            return result
        else:
            print(f"❌ {label} failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ {label} error: {e}")
        return None

if __name__ == "__main__":
    print("🎯 Generating diverse customer predictions...")
    
    # Generate high-risk predictions
    for i, customer in enumerate(high_risk_customers):
        make_prediction(customer, f"High-risk customer {i+1}")
        time.sleep(1)
    
    print(f"\n✅ Diverse predictions generated!")
    print(f"📊 Check your Grafana dashboard for updated metrics")