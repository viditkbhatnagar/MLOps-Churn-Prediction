#!/usr/bin/env python3
"""
Generate continuous metrics for better rate() calculations
"""

import time
import requests
import random

def generate_single_prediction():
    sample_customer = {
        "gender": random.choice(["Male", "Female"]),
        "SeniorCitizen": random.choice([0, 1]),
        "Partner": random.choice(["Yes", "No"]),
        "Dependents": random.choice(["Yes", "No"]),
        "tenure": random.randint(1, 72),
        "PhoneService": "Yes",
        "MultipleLines": random.choice(["Yes", "No"]),
        "InternetService": random.choice(["DSL", "Fiber optic", "No"]),
        "OnlineSecurity": random.choice(["Yes", "No"]),
        "OnlineBackup": random.choice(["Yes", "No"]),
        "DeviceProtection": random.choice(["Yes", "No"]),
        "TechSupport": random.choice(["Yes", "No"]),
        "StreamingTV": random.choice(["Yes", "No"]),
        "StreamingMovies": random.choice(["Yes", "No"]),
        "Contract": random.choice(["Month-to-month", "One year", "Two year"]),
        "PaperlessBilling": random.choice(["Yes", "No"]),
        "PaymentMethod": random.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"]),
        "MonthlyCharges": round(random.uniform(20, 120), 2),
        "TotalCharges": round(random.uniform(100, 8000), 2)
    }
    
    try:
        response = requests.post("http://localhost:8000/predict", json=sample_customer)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['churn_prediction']} ({result['risk_level']}) - {result['churn_probability']:.3f}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    print("🔄 Generating continuous metrics for Grafana...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            generate_single_prediction()
            time.sleep(2)  # One prediction every 2 seconds
    except KeyboardInterrupt:
        print("\n⏹️ Stopped generating metrics")