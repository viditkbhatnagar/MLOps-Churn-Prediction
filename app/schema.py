# app/schema.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List


class CustomerData(BaseModel):
    """Schema for customer input data"""

    gender: str = Field(..., description="Customer gender (Male/Female)")
    SeniorCitizen: int = Field(
        ..., ge=0, le=1, description="Senior citizen status (0/1)"
    )
    Partner: str = Field(..., description="Has partner (Yes/No)")
    Dependents: str = Field(..., description="Has dependents (Yes/No)")
    tenure: int = Field(..., ge=0, le=100, description="Months with company")
    PhoneService: str = Field(..., description="Has phone service (Yes/No)")
    MultipleLines: str = Field(
        ..., description="Multiple lines (Yes/No/No phone service)"
    )
    InternetService: str = Field(
        ..., description="Internet service type (DSL/Fiber optic/No)"
    )
    OnlineSecurity: str = Field(
        ..., description="Online security (Yes/No/No internet service)"
    )
    OnlineBackup: str = Field(
        ..., description="Online backup (Yes/No/No internet service)"
    )
    DeviceProtection: str = Field(
        ..., description="Device protection (Yes/No/No internet service)"
    )
    TechSupport: str = Field(
        ..., description="Tech support (Yes/No/No internet service)"
    )
    StreamingTV: str = Field(
        ..., description="Streaming TV (Yes/No/No internet service)"
    )
    StreamingMovies: str = Field(
        ..., description="Streaming movies (Yes/No/No internet service)"
    )
    Contract: str = Field(
        ..., description="Contract type (Month-to-month/One year/Two year)"
    )
    PaperlessBilling: str = Field(..., description="Paperless billing (Yes/No)")
    PaymentMethod: str = Field(..., description="Payment method")
    MonthlyCharges: float = Field(..., gt=0, description="Monthly charges amount")
    TotalCharges: float = Field(..., gt=0, description="Total charges amount")

    @validator("gender")
    def validate_gender(cls, v):
        if v not in ["Male", "Female"]:
            raise ValueError("Gender must be Male or Female")
        return v

    @validator("Partner", "Dependents", "PhoneService", "PaperlessBilling")
    def validate_yes_no(cls, v):
        if v not in ["Yes", "No"]:
            raise ValueError("Value must be Yes or No")
        return v

    @validator("Contract")
    def validate_contract(cls, v):
        valid_contracts = ["Month-to-month", "One year", "Two year"]
        if v not in valid_contracts:
            raise ValueError(f'Contract must be one of: {", ".join(valid_contracts)}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
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
                "TotalCharges": 844.20,
            }
        }


class PredictionResponse(BaseModel):
    """Schema for prediction response"""

    customer_id: str = Field(..., description="Unique customer identifier")
    churn_probability: float = Field(
        ..., ge=0, le=1, description="Probability of churn"
    )
    churn_prediction: str = Field(..., description="Churn prediction (Yes/No)")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence")
    risk_level: str = Field(..., description="Risk level (Low/Medium/High)")


class BatchPredictionRequest(BaseModel):
    """Schema for batch prediction request"""

    customers: List[CustomerData] = Field(
        ..., description="List of customers to predict"
    )


class BatchPredictionResponse(BaseModel):
    """Schema for batch prediction response"""

    predictions: List[PredictionResponse] = Field(
        ..., description="List of predictions"
    )
    total_processed: int = Field(..., description="Total number of customers processed")
    high_risk_count: int = Field(..., description="Number of high-risk customers")


# Update the HealthResponse class in app/schema.py to fix the warning


class HealthResponse(BaseModel):
    """Schema for health check response"""

    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Model loading status")
    version: str = Field(..., description="API version")

    model_config = {"protected_namespaces": ()}  # This fixes the warning
