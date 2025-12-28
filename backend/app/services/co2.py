DEFAULT_EMISSION_FACTOR = 0.475  # kg CO2 per kWh default, configurable per region

def co2_avoided_kgs(energy_kwh: float, emission_factor: float = DEFAULT_EMISSION_FACTOR) -> float:
    return energy_kwh * emission_factor
