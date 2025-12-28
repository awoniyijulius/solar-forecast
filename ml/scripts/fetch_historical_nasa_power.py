# ml/scripts/fetch_historical_nasa_power.py
import os
import requests
import pandas as pd
from datetime import datetime

OUT_DIR = os.environ.get("OUT_DIR", "./ml/data")
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_nasa_power(lat, lon, start="2015-01-01", end=None, out_name=None):
    if end is None:
        end = datetime.utcnow().strftime("%Y-%m-%d")
    params = {
        "start": start,
        "end": end,
        "latitude": lat,
        "longitude": lon,
        "community": "RE",
        "parameters": "ALLSKY_SFC_SW_DWN,ALLSKY_SFC_LW_DWN,ALLSKY_SFC_PAR,CLD_FRAC",
        "format": "CSV"
    }
    url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    out_name = out_name or f"nasa_power_{lat}_{lon}.csv"
    path = os.path.join(OUT_DIR, out_name)
    with open(path, "wb") as f:
        f.write(r.content)
    print("Saved", path)
    return path

if __name__ == "__main__":
    # example: Paris
    fetch_nasa_power(48.8566, 2.3522, start="2018-01-01", end=None, out_name="nasa_paris.csv")
