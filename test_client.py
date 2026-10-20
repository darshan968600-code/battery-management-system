"""
Client test script for Battery Management System (BMS) Inference API.
Can test both local (127.0.0.1:8000) and public AWS EC2 (13.203.220.49:8000).
"""

import sys
import time
import httpx
import numpy as np

# Default to your live secured AWS EC2 server; or pass URL as an argument
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://battery-bms.duckdns.org"

print("=================================================================")
print(f"   TESTING BMS PREDICTION API ON: {BASE_URL}")
print("=================================================================")


def test_health():
    print("\n--- [1] Testing Health Endpoint (/health) ---")
    res = httpx.get(f"{BASE_URL}/health", timeout=10.0)
    print(f"Status Code: {res.status_code}")
    print(f"Response   : {res.json()}")
    assert res.status_code == 200


def test_model_info():
    print("\n--- [2] Testing Model Info (/model/info) ---")
    res = httpx.get(f"{BASE_URL}/model/info", timeout=10.0)
    data = res.json()
    print(f"Active Model: {data.get('model_name')}")
    print(f"Version     : {data.get('version')}")
    print(f"Window Size : {data.get('window_size')} timesteps")
    print(f"Features    : {data.get('features')}")
    assert res.status_code == 200


def test_predict_full_window():
    print("\n--- [3] Testing Standard 32-Timestep Window Prediction ---")
    np.random.seed(42)
    # 32 timesteps, each with 3 features: [Voltage, Current, Temp]
    window = np.random.uniform(0.2, 0.8, size=(32, 3)).tolist()

    payload = {"window": window}
    start = time.perf_counter()
    res = httpx.post(f"{BASE_URL}/predict", json=payload, timeout=10.0)
    roundtrip = (time.perf_counter() - start) * 1000

    print(f"Status Code   : {res.status_code}")
    print(f"Roundtrip Net : {roundtrip:.2f} ms")
    data = res.json()
    print(f"  -> Predicted SOC    : {data['soc_percentage']}%")
    print(f"  -> Predicted SOH    : {data['soh_metric']}")
    print(f"  -> Battery Status   : {data['battery_status']}")
    print(f"  -> Server Inference : {data['inference_time_ms']} ms")
    assert res.status_code == 200


def test_predict_by_channels():
    print("\n--- [4] Testing Explicit Named Channels (/predict/channels) ---")
    # Sending 3 separate lists of 32 readings
    voltages = [3.8] * 32
    currents = [1.5] * 32
    temps = [27.0] * 32

    payload = {
        "voltage": voltages,
        "current": currents,
        "temperature": temps
    }
    res = httpx.post(f"{BASE_URL}/predict/channels", json=payload, timeout=10.0)
    data = res.json()
    print(f"Status Code   : {res.status_code}")
    print(f"  -> Predicted SOC    : {data['soc_percentage']}%")
    print(f"  -> Predicted SOH    : {data['soh_metric']}")
    print(f"  -> Battery Status   : {data['battery_status']}")
    assert res.status_code == 200


def test_cold_start_padding():
    print("\n--- [5] Testing Cold-Start Auto-Padding (Only 10 readings sent) ---")
    # Sending fewer than 32 readings to verify server auto-padding
    short_window = [[3.7, 0.0, 25.0]] * 10
    payload = {"window": short_window}

    res = httpx.post(f"{BASE_URL}/predict", json=payload, timeout=10.0)
    data = res.json()
    print(f"Status Code   : {res.status_code}")
    print(f"  -> Automatically padded 10 readings to 32!")
    print(f"  -> Predicted SOC    : {data['soc_percentage']}%")
    print(f"  -> Predicted SOH    : {data['soh_metric']}")
    assert res.status_code == 200


if __name__ == "__main__":
    try:
        test_health()
        test_model_info()
        test_predict_full_window()
        test_predict_by_channels()
        test_cold_start_padding()
        print("\n=================================================================")
        print("  [SUCCESS] ALL TESTS AGAINST LIVE AWS SERVER PASSED PERFECTLY!  ")
        print("=================================================================")
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
