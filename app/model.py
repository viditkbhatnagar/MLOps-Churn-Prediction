# app/model.py

import joblib
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChurnPredictor:
    """Churn prediction model handler"""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.model_path = Path(__file__).parent

    def load_model(self) -> bool:
        """Load the trained model, scaler, and feature names"""
        try:
            # Load model
            model_file = self.model_path / "churn_model.pkl"
            if not model_file.exists():
                logger.error(f"Model file not found: {model_file}")
                return False
            self.model = joblib.load(model_file)
            logger.info("Model loaded successfully")

            # Load scaler
            scaler_file = self.model_path / "scaler.pkl"
            if not scaler_file.exists():
                logger.error(f"Scaler file not found: {scaler_file}")
                return False
            self.scaler = joblib.load(scaler_file)
            logger.info("Scaler loaded successfully")

            # Load feature names
            features_file = self.model_path / "feature_names.pkl"
            if not features_file.exists():
                logger.error(f"Feature names file not found: {features_file}")
                return False
            self.feature_names = joblib.load(features_file)
            logger.info("Feature names loaded successfully")

            return True

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False

    def preprocess_input(self, customer_data: Dict) -> pd.DataFrame:
        """Preprocess input data to match training format"""
        # Create DataFrame
        df = pd.DataFrame([customer_data])

        # Binary encoding
        binary_mappings = {
            "gender": {"Male": 1, "Female": 0},
            "Partner": {"Yes": 1, "No": 0},
            "Dependents": {"Yes": 1, "No": 0},
            "PhoneService": {"Yes": 1, "No": 0},
            "PaperlessBilling": {"Yes": 1, "No": 0},
        }

        for col, mapping in binary_mappings.items():
            if col in df.columns:
                df[col] = df[col].map(mapping)

        # One-hot encoding for categorical columns
        categorical_cols = [
            "MultipleLines",
            "InternetService",
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
            "Contract",
            "PaymentMethod",
        ]

        # Get dummies
        df_encoded = pd.get_dummies(df, columns=categorical_cols)

        # Feature engineering
        df_encoded["tenure_MonthlyCharges"] = (
            df_encoded["tenure"] * df_encoded["MonthlyCharges"]
        )
        df_encoded["TotalCharges_per_Month"] = df_encoded["TotalCharges"] / (
            df_encoded["tenure"] + 1
        )

        # Ensure all features from training are present
        for feature in self.feature_names:
            if feature not in df_encoded.columns:
                df_encoded[feature] = 0

        # Select only the features used during training
        df_final = df_encoded[self.feature_names]

        return df_final

    def predict(self, customer_data: Dict) -> Tuple[float, str, float, str]:
        """Make prediction for a single customer"""
        try:
            # Preprocess data
            df = self.preprocess_input(customer_data)

            # Scale features
            X_scaled = self.scaler.transform(df)

            # Get prediction and probability
            prediction = self.model.predict(X_scaled)[0]
            probability = self.model.predict_proba(X_scaled)[0, 1]

            # Determine risk level
            if probability < 0.3:
                risk_level = "Low"
            elif probability < 0.7:
                risk_level = "Medium"
            else:
                risk_level = "High"

            # Calculate confidence (distance from 0.5)
            confidence = abs(probability - 0.5) * 2

            return (
                float(probability),
                "Yes" if prediction == 1 else "No",
                float(confidence),
                risk_level,
            )

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise

    def predict_batch(self, customers: List[Dict]) -> List[Dict]:
        """Make predictions for multiple customers"""
        results = []

        for i, customer in enumerate(customers):
            try:
                prob, pred, conf, risk = self.predict(customer)
                results.append(
                    {
                        "customer_id": f"CUST_{i+1:04d}",
                        "churn_probability": prob,
                        "churn_prediction": pred,
                        "confidence": conf,
                        "risk_level": risk,
                    }
                )
            except Exception as e:
                logger.error(f"Error predicting customer {i}: {str(e)}")
                results.append({"customer_id": f"CUST_{i+1:04d}", "error": str(e)})

        return results


# Create global predictor instance
predictor = ChurnPredictor()
