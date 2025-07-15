#!/usr/bin/env python3
"""
Load testing script for the churn prediction API
"""

import requests
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

API_URL = "http://localhost:8000"

def generate_random_customer():
    """Generate random customer data for testing"""
    return {
        "gender": random.choice(["Male", "Female"]),
        "SeniorCitizen": random.choice([0, 1]),
        "Partner": random.choice(["Yes", "No"]),
        "Dependents": random.choice(["Yes", "No"]),
        "tenure": random.randint(0, 72),
        "PhoneService": random.choice(["Yes", "No"]),
        "MultipleLines": random.choice(["Yes", "No", "No phone service"]),
        "InternetService": random.choice(["DSL", "Fiber optic", "No"]),
        "OnlineSecurity": random.choice(["Yes", "No", "No internet service"]),
        "OnlineBackup": random.choice(["Yes", "No", "No internet service"]),
        "DeviceProtection": random.choice(["Yes", "No", "No internet service"]),
        "TechSupport": random.choice(["Yes", "No", "No internet service"]),
        "StreamingTV": random.choice(["Yes", "No", "No internet service"]),
        "StreamingMovies": random.choice(["Yes", "No", "No internet service"]),
        "Contract": random.choice(["Month-to-month", "One year", "Two year"]),
        "PaperlessBilling": random.choice(["Yes", "No"]),
        "PaymentMethod": random.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"]),
        "MonthlyCharges": round(random.uniform(20, 120), 2),
        "TotalCharges": round(random.uniform(20, 8000), 2)
    }

def make_prediction():
    """Make a single prediction request"""
    start_time = time.time()
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=generate_random_customer(),
            headers={"Content-Type": "application/json"}
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            return True, elapsed_time
        else:
            return False, elapsed_time
    except Exception as e:
        return False, time.time() - start_time

def load_test(num_requests=100, num_workers=10):
    """Run load test"""
    print(f"Starting load test with {num_requests} requests using {num_workers} workers...")
    
    success_count = 0
    response_times = []
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(make_prediction) for _ in range(num_requests)]
        
        for future in as_completed(futures):
            success, elapsed_time = future.result()
            if success:
                success_count += 1
            response_times.append(elapsed_time)
    
    # Calculate statistics
    success_rate = (success_count / num_requests) * 100
    avg_response_time = statistics.mean(response_times)
    p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
    
    print(f"\nLoad Test Results:")
    print(f"Total Requests: {num_requests}")
    print(f"Successful Requests: {success_count}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Average Response Time: {avg_response_time:.3f}s")
    print(f"95th Percentile Response Time: {p95_response_time:.3f}s")

if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("API is healthy, starting load test...")
            load_test(num_requests=1000, num_workers=20)
        else:
            print("API health check failed!")
    except Exception as e:
        print(f"Cannot connect to API: {e}")