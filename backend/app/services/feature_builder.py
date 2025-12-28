import pandas as pd
from typing import Dict, Any
import numpy as np
import datetime

def build_features(forecast_json: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert Open-Meteo hourly forecast JSON into a feature DataFrame
    with columns used by the model.
    """
    hourly = forecast_json.get("hourly", {})
    times = hourly.get("time", [])
    df = pd.DataFrame({
        "time": pd.to_datetime(times),
        "temp": hourly.get("temperature_2m", []),
        "cloud": hourly.get("cloudcover", []),
        "radiation": hourly.get("shortwave_radiation", []),
        "uv": hourly.get("uv_index", [])
    })
    df["hour"] = df["time"].dt.hour
    df["dayofyear"] = df["time"].dt.dayofyear
    # simple engineered features
    df["cloud_lag1"] = df["cloud"].shift(1).bfill()
    df["temp_diff"] = df["temp"] - df["temp"].rolling(3, min_periods=1).mean()
    return df
