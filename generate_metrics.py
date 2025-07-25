#!/usr/bin/env python3
"""
Script to generate sample API requests to populate Prometheus metrics
"""

import requests
import json
import time
import random

API_BASE_URL = "http://localhost:8000"

# Sample customer data variations
sample_customers = [
    {
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
    },
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
    },
    {
        "gender": "Male",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 6,
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
        "MonthlyCharges": 95.00,
        "TotalCharges": 570.00
    }
]

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def make_single_prediction(customer_data):
    """Make a single prediction"""
    try:
        response = requests.post(f"{API_BASE_URL}/predict", json=customer_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prediction: {result['churn_prediction']} (Risk: {result['risk_level']}, Prob: {result['churn_probability']:.3f})")
            return result
        else:
            print(f"❌ Prediction failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def make_batch_prediction(customers):
    """Make batch predictions"""
    try:
        batch_data = {"customers": customers}
        response = requests.post(f"{API_BASE_URL}/batch_predict", json=batch_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch prediction: {result['total_processed']} customers, {result['high_risk_count']} high risk")
            return result
        else:
            print(f"❌ Batch prediction failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Batch request failed: {e}")
        return None

def generate_metrics_data():
    """Generate sample data to populate metrics"""
    print("🚀 Starting metrics generation...")
    
    # Check if API is healthy
    if not test_health():
        print("❌ API is not healthy. Make sure your FastAPI server is running.")
        return
    
    print(f"\n📊 Generating metrics data...")
    print("This will create data for Prometheus and Grafana dashboards\n")
    
    # Generate individual predictions
    print("1️⃣ Making individual predictions...")
    for i in range(10):
        customer = random.choice(sample_customers).copy()
        # Add some randomness
        customer['tenure'] = random.randint(1, 72)
        customer['MonthlyCharges'] = round(random.uniform(20, 120), 2)
        customer['TotalCharges'] = round(customer['tenure'] * customer['MonthlyCharges'] * random.uniform(0.8, 1.2), 2)
        
        make_single_prediction(customer)
        time.sleep(0.5)  # Small delay
    
    # Generate batch predictions
    print(f"\n2️⃣ Making batch predictions...")
    for i in range(3):
        batch_customers = random.sample(sample_customers, 2)
        make_batch_prediction(batch_customers)
        time.sleep(1)
    
    # Generate some varied requests
    print(f"\n3️⃣ Making varied requests...")
    for i in range(15):
        if random.choice([True, False]):
            # Single prediction
            customer = random.choice(sample_customers).copy()
            # Vary some parameters to get different risk levels
            if random.random() < 0.3:  # 30% chance of high-risk profile
                customer['Contract'] = 'Month-to-month'
                customer['tenure'] = random.randint(1, 12)
                customer['PaymentMethod'] = 'Electronic check'
            
            make_single_prediction(customer)
        else:
            # Batch prediction
            batch_size = random.randint(1, 3)
            batch_customers = random.choices(sample_customers, k=batch_size)
            make_batch_prediction(batch_customers)
        
        time.sleep(random.uniform(0.3, 1))
    
    print(f"\n✅ Metrics generation complete!")
    print(f"📈 You should now see data in:")
    print(f"   - Prometheus: http://localhost:9090")
    print(f"   - Grafana: http://localhost:3000")

if __name__ == "__main__":
    generate_metrics_data()