import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import lightgbm as lgb
import joblib
from preprocess import load_nasa_power_csv, create_features
import os
import json
from datetime import datetime

DATA_CSV = os.environ.get("DATA_CSV", "ml/data/nasa_power_sample.csv")
MODEL_OUT = os.environ.get("MODEL_OUT", "ml/artifacts/lightgbm_model.joblib")
METRICS_OUT = os.environ.get("METRICS_OUT", "ml/artifacts/metrics.json")

def train():
    print(f"[{datetime.now().isoformat()}] 🚀 PRODUCTION TRAINING SEQUENCE STARTED")
    
    # Create artifacts directory
    os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
    
    # Load and prepare data
    if not os.path.exists(DATA_CSV):
        print(f"❌ Error: Data file {DATA_CSV} not found.")
        return
        
    print(f"📊 Loading dataset: {DATA_CSV}")
    df = load_nasa_power_csv(DATA_CSV)
    df = create_features(df)
    
    # Target: Actual Power (kW). Using 0.01 factor for a standard 10kWp system.
    # (1000 W/m2 * 0.01 = 10kW peak)
    y = np.maximum(0, df["ghi"] * 0.01) 
    
    # Feature Engineering
    features = ["temp", "cloudcover", "ghi_lag1", "ghi_roll3", "hour", "dayofyear"]
    X = df[features]
    
    print(f"📈 Feature Matrix: {X.shape}")
    
    # Train-test split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # LightGBM Parameters - Standard production config
    params = {
        "objective": "regression",
        "metric": "rmse",
        "verbosity": -1,
        "learning_rate": 0.05,
        "num_leaves": 31,
        "feature_fraction": 0.9,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "min_data_in_leaf": 3 # Adjusted for small sample
    }
    
    train_data = lgb.Dataset(X_train, label=y_train)
    val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
    
    print("🧠 Optimizing Gradient Boosting Machine...")
    model = lgb.train(
        params, 
        train_data, 
        valid_sets=[train_data, val_data],
        num_boost_round=500, 
        callbacks=[lgb.early_stopping(stopping_rounds=30)]
    )
    
    # Final Evaluation
    y_pred_val = model.predict(X_val)
    r2 = r2_score(y_val, y_pred_val)
    mse = mean_squared_error(y_val, y_pred_val)
    rmse = np.sqrt(mse)
    
    metrics = {
        "validation": {
            "r2": float(r2),
            "rmse": float(rmse),
            "mae": float(mean_absolute_error(y_val, y_pred_val))
        },
        "metadata": {
            "trained_at": datetime.now().isoformat(),
            "model_type": "LightGBM",
            "version": "1.0.2"
        }
    }
    
    print("\n" + "="*30)
    print(f"🏆 R² SCORE:  {r2:.4f}")
    print(f"🏆 RMSE:      {rmse:.4f}")
    print("="*30 + "\n")
    
    # Save Artifacts
    joblib.dump(model, MODEL_OUT)
    with open(METRICS_OUT, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"💾 Model artifact saved to: {MODEL_OUT}")

if __name__ == "__main__":
    train()
