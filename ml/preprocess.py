import pandas as pd
import numpy as np

def load_nasa_power_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["time"])
    # expected columns: time, ghi, dni, dhi, temp, cloudcover, etc.
    df = df.sort_values("time")
    return df

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    df["hour"] = df["time"].dt.hour
    df["dayofyear"] = df["time"].dt.dayofyear
    df["ghi_lag1"] = df["ghi"].shift(1).bfill()
    df["ghi_roll3"] = df["ghi"].rolling(3, min_periods=1).mean()
    return df.dropna()
