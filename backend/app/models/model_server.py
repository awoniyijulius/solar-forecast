import joblib
import numpy as np
import pandas as pd
import os
from typing import Dict, Any

MODEL_PATH_DEFAULT = os.environ.get("MODEL_PATH", "./ml/artifacts/lightgbm_model.joblib")

class ModelServer:
    def __init__(self, model_path: str = MODEL_PATH_DEFAULT):
        self.model_path = model_path
        self.model = None
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                print(f"✅ Loaded model from {model_path}")
            except Exception as e:
                print(f"⚠️ Failed to load model at {model_path}: {e}")
                self.model = None
        else:
            print(f"ℹ️ No model artifact found at {model_path}; using heuristic fallback")

    def predict_24h(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run inference with physical guardrails. 
        Zeroes out production when radiation is 0 (nighttime).
        """
        try:
            # Ensure we have radiation data for the night check
            rad_col = "radiation" if "radiation" in df.columns else None
            
            if self.model:
                features_map = {
                    "temp": "temp",
                    "cloud": "cloud",
                    "radiation": "ghi"
                }
                X = df.rename(columns=features_map).copy()
                req_cols = ["temp", "cloud", "ghi_lag1", "ghi_roll3", "hour", "dayofyear"]
                
                # Check for lag/rolling features if not pre-computed
                if "ghi_lag1" not in X.columns:
                    X["ghi_lag1"] = X["ghi"].shift(1).fillna(0)
                if "ghi_roll3" not in X.columns:
                    X["ghi_roll3"] = X["ghi"].rolling(3, min_periods=1).mean()

                for col in req_cols:
                    if col not in X.columns:
                        X[col] = 0
                
                y_pred = self.model.predict(X[req_cols])
                y_pred = np.maximum(0, y_pred)
            else:
                # Heuristic fallback
                rad = df["radiation"] if rad_col else np.zeros(len(df))
                cloud = df["cloudcover"] if "cloudcover" in df.columns else np.zeros(len(df))
                
                # Yield = Rad (W/m2) * Area (m2) * Efficiency
                # For a typical 10kW system (approx 50m2 at 20% efficiency)
                # Max rad is ~1000 W/m2 -> 1000 * 50 * 0.2 = 10,000 W = 10 kW
                # So factor is 0.01 for a 10kW peak system
                y_pred = (rad * 0.01) * (1 - (cloud / 150.0))
                y_pred = np.maximum(0.0, y_pred)
            
            # PHYSICAL GUARDRAIL: Solar panels DO NOT produce energy at night (Rad = 0)
            if rad_col:
                y_pred = np.where(df[rad_col] <= 0, 0.0, y_pred)
                
            conf = y_pred * 0.12 # 12% relative uncertainty
            
            return {
                "hours": df["time"].tolist(),
                "pred_kwh": [round(float(x), 3) for x in y_pred],
                "confidence": [round(float(x), 3) for x in conf],
                "model_version": "1.0-LGBM" if self.model else "V0-Heuristic"
            }
        except Exception as e:
            print(f"❌ Prediction Error: {e}")
            return {"hours": [], "pred_kwh": [], "confidence": []}
