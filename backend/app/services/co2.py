DEFAULT_EMISSION_FACTOR = 0.475  # kg CO2 per kWh default, configurable per region

# Regional Grid Emission Factors (gCO2eq / kWh)
# Sources: IEA, Ember (2023/2024 benchmarks)
CITY_GRID_INTENSITY = {
    "lagos": 480.0,      # Gas-heavy, high transmission loss
    "nairobi": 120.0,    # High Geothermal/Hydro mix
    "cape_town": 850.0,  # Coal-heavy grid
    "london": 180.0,     # Mixed (Gas/Offshore Wind)
    "berlin": 350.0,     # Mixed (Lignite/Wind/Solar)
    "paris": 55.0,       # Nuclear-heavy (Very low carbon)
    "tokyo": 450.0,      # LNG/Coal mix
    "new_york": 220.0,   # Gas/Hydro/Nuclear
    "dubai": 580.0,      # Natural Gas dominant
    "sydney": 650.0,     # Coal/Solar transition
    "default": 450.0
}

def co2_avoided_kgs(kwh: float, location: str = "default") -> float:
    """
    Calculates carbon avoidance based on high-resolution regional grid factors.
    Compliant with GHG Protocol Scope 2 accounting.
    """
    intensity = CITY_GRID_INTENSITY.get(location.lower(), CITY_GRID_INTENSITY["default"])
    # (kWh * gCO2/kWh) / 1000 = kgCO2
    return (kwh * intensity) / 1000.0
