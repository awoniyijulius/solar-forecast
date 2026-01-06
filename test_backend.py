#!/usr/bin/env python3
"""
Quick test script to verify backend components work correctly.
Run this before starting Docker Compose.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all backend imports work"""
    print("Testing backend imports...")
    try:
        from app.services import weather_client, feature_builder, co2, cache
        from app.models.model_server import ModelServer
        from app.api import predictions, admin
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_co2_calculation():
    """Test CO₂ calculation"""
    print("\nTesting CO₂ calculation...")
    try:
        from app.services.co2 import co2_avoided_kgs
        
        # Test with 10 kWh
        result = co2_avoided_kgs(10.0)
        expected = 10.0 * 0.450  # 4.50 kg (Default grid intensity 450g)
        
        if abs(result - expected) < 0.01:
            print(f"✅ CO₂ calculation correct: {result:.2f} kg for 10 kWh")
            return True
        else:
            print(f"❌ CO₂ calculation incorrect: got {result}, expected {expected}")
            return False
    except Exception as e:
        print(f"❌ CO₂ test error: {e}")
        return False

def test_model_server():
    """Test model server initialization"""
    print("\nTesting model server...")
    try:
        from app.models.model_server import ModelServer
        
        ms = ModelServer()
        print(f"✅ Model server initialized (model loaded: {ms.model is not None})")
        
        if ms.model is None:
            print("ℹ️  No model artifact found - will use heuristic fallback")
        
        return True
    except Exception as e:
        print(f"❌ Model server error: {e}")
        return False

def test_feature_builder():
    """Test feature builder"""
    print("\nTesting feature builder...")
    try:
        from app.services.feature_builder import build_features
        import pandas as pd
        
        # Mock forecast data
        mock_forecast = {
            "hourly": {
                "time": ["2024-01-01T00:00", "2024-01-01T01:00", "2024-01-01T02:00"],
                "temperature_2m": [15.0, 14.5, 14.0],
                "cloudcover": [50, 55, 60],
                "shortwave_radiation": [0, 0, 0],
                "uv_index": [0, 0, 0]
            }
        }
        
        df = build_features(mock_forecast)
        
        if len(df) == 3 and "hour" in df.columns and "cloud" in df.columns:
            print(f"✅ Feature builder works: {len(df)} rows, {len(df.columns)} features")
            return True
        else:
            print(f"❌ Feature builder output unexpected")
            return False
    except Exception as e:
        print(f"❌ Feature builder error: {e}")
        return False

def test_theoretical_fallback():
    """Test theoretical fallback physics"""
    print("\nTesting theoretical fallback...")
    try:
        from app.services.weather_client import get_theoretical_fallback
        from datetime import datetime
        
        # Test Case 1: Prime Meridian (London/Accra). NOON UTC should be SUNNY.
        # lon=0.0 -> offset=0. Local = UTC.
        res = get_theoretical_fallback(0.0, 0.0)
        times = res["hourly"]["time"]
        rads = res["hourly"]["shortwave_radiation"]
        
        # Find index for 12:00 UTC today/tomorrow
        noon_idx = -1
        midnight_idx = -1
        
        for i, t_str in enumerate(times):
            dt = datetime.fromisoformat(t_str)
            if dt.hour == 12 and noon_idx == -1:
                noon_idx = i
            if dt.hour == 0 and midnight_idx == -1:
                midnight_idx = i
                
        if noon_idx == -1: 
            print("⚠️ Could not find noon index")
            return False
            
        print(f"  [Lon 0] Rad at 12:00 UTC: {rads[noon_idx]:.1f}")
        print(f"  [Lon 0] Rad at 00:00 UTC: {rads[midnight_idx]:.1f}")
        
        if rads[noon_idx] < 100:
            print("❌ Lon 0: Noon should be sunny!")
            return False
        if rads[midnight_idx] > 10:
            print("❌ Lon 0: Midnight should be dark!")
            return False
            
        # Test Case 2: 180 deg East (Fijiish). NOON UTC is MIDNIGHT Local.
        # lon=180 -> offset +12. 
        # 12:00 UTC + 12 = 24:00 (Midnight). Should be DARK.
        # 00:00 UTC + 12 = 12:00 (Noon). Should be SUNNY.
        
        res_fiji = get_theoretical_fallback(0.0, 180.0)
        rads_fiji = res_fiji["hourly"]["shortwave_radiation"]
        
        print(f"  [Lon 180] Rad at 12:00 UTC: {rads_fiji[noon_idx]:.1f}")
        print(f"  [Lon 180] Rad at 00:00 UTC: {rads_fiji[midnight_idx]:.1f}")

        if rads_fiji[noon_idx] > 10:
             print("❌ Lon 180: 12:00 UTC (Midnight Local) should be dark!")
             return False
        if rads_fiji[midnight_idx] < 100:
             print("❌ Lon 180: 00:00 UTC (Noon Local) should be sunny!")
             return False

        print("✅ Theoretical physics verified correctly")
        return True

    except Exception as e:
        print(f"❌ Fallback test error: {e}")
        return False

def main():
    print("="*60)
    print("SolarSight Backend Component Tests")
    print("="*60)
    
    tests = [
        test_imports,
        test_co2_calculation,
        test_model_server,
        test_theoretical_fallback,
        test_feature_builder
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "="*60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*60)
    
    if all(results):
        print("\n✅ All tests passed! Ready to start Docker Compose.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
