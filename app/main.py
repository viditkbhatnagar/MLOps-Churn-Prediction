# app/main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import time
import logging
from contextlib import asynccontextmanager
import uuid

from .schema import (
    CustomerData,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
)
from .model import predictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    if not predictor.load_model():
        logger.error("Failed to load model!")
    else:
        logger.info("Model loaded successfully!")
    yield
    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Churn Prediction API",
    description="MLOps-powered customer churn prediction service",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus instrumentation
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Custom metrics
from prometheus_client import Counter, Histogram, Gauge

prediction_counter = Counter(
    "churn_predictions_total",
    "Total number of churn predictions",
    ["prediction", "risk_level"],
)

prediction_latency = Histogram(
    "churn_prediction_latency_seconds", "Latency of churn predictions"
)

high_risk_gauge = Gauge(
    "churn_high_risk_customers", "Number of high risk customers in current batch"
)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Churn Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "batch_predict": "/batch_predict",
            "metrics": "/metrics",
            "docs": "/docs",
        },
    }


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    model_loaded = predictor.model is not None
    return HealthResponse(
        status="healthy" if model_loaded else "unhealthy",
        model_loaded=model_loaded,
        version="1.0.0",
    )


# Single prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
async def predict(customer: CustomerData):
    """Make churn prediction for a single customer"""
    start_time = time.time()

    try:
        # Check if model is loaded
        if predictor.model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")

        # Make prediction
        probability, prediction, confidence, risk_level = predictor.predict(
            customer.dict()
        )

        # Update metrics
        prediction_counter.labels(prediction=prediction, risk_level=risk_level).inc()
        prediction_latency.observe(time.time() - start_time)

        # Generate customer ID
        customer_id = f"CUST_{str(uuid.uuid4())[:8].upper()}"

        logger.info(
            f"Prediction made for {customer_id}: {prediction} (risk: {risk_level})"
        )

        return PredictionResponse(
            customer_id=customer_id,
            churn_probability=probability,
            churn_prediction=prediction,
            confidence=confidence,
            risk_level=risk_level,
        )

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Batch prediction endpoint
@app.post("/batch_predict", response_model=BatchPredictionResponse)
async def batch_predict(request: BatchPredictionRequest):
    """Make churn predictions for multiple customers"""
    start_time = time.time()

    try:
        # Check if model is loaded
        if predictor.model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")

        # Convert customers to dict format
        customers_data = [customer.dict() for customer in request.customers]

        # Make predictions
        predictions_data = predictor.predict_batch(customers_data)

        # Convert to response format
        predictions = []
        high_risk_count = 0

        for pred_data in predictions_data:
            if "error" not in pred_data:
                predictions.append(PredictionResponse(**pred_data))
                if pred_data["risk_level"] == "High":
                    high_risk_count += 1
                # Update metrics
                prediction_counter.labels(
                    prediction=pred_data["churn_prediction"],
                    risk_level=pred_data["risk_level"],
                ).inc()

        # Update gauges
        high_risk_gauge.set(high_risk_count)
        prediction_latency.observe(time.time() - start_time)

        logger.info(
            f"Batch prediction completed: {len(predictions)} customers, {high_risk_count} high risk"
        )

        return BatchPredictionResponse(
            predictions=predictions,
            total_processed=len(predictions),
            high_risk_count=high_risk_count,
        )

    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Model info endpoint
@app.get("/model/info")
async def model_info():
    """Get information about the loaded model"""
    if predictor.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "model_type": type(predictor.model).__name__,
        "feature_count": len(predictor.feature_names) if predictor.feature_names else 0,
        "features": predictor.feature_names[:10]
        if predictor.feature_names
        else [],  # Show first 10 features
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
