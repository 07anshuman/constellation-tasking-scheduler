import requests
import json

payload = {
    "scenario": {
        "start_time": "2025-07-17T00:00:00Z",
        "duration_minutes": 180,
        "timestep_sec": 60,
        "satellites": [
            {
                "name": "ISS",
                "tle": [
                    "1 25544U 98067A   20252.54846065  .00001264  00000-0  29621-4 0  9993",
                    "2 25544  51.6445  49.2431 0001235 131.1758 284.5727 15.49211630243154"
                ],
                "battery_wh": 1000.0,
                "initial_battery_wh": 500.0,
                "charge_rate_w": 400.0,
                "imaging_power_w": 50.0,
                "downlink_power_w": 40.0,
                "idle_power_w": 5.0,
                "storage_capacity_mb": 1000.0,
                "initial_storage_mb": 0.0,
                "downlink_bandwidth_mbps": 50.0
            }
            # ... more satellites if needed
        ],
        "ground_stations": [
            {
                "name": "DefaultGS",
                "lat": 31.2304,
                "lon": 121.4737,
                "alt_m": 10
            }
        ]
    },
    "targets": [
        {
            "name": "Shanghai",
            "lat": 31.2304,
            "lon": 121.4737,
            "priority": 3,
            "revisit_hours": 4,
            "image_size_mb": 40,
            "image_energy_wh": 4
        }
        # ... more targets if needed
    ],
    "output_path": "outputs/api_test.csv"
}

resp = requests.post("http://127.0.0.1:8000/simulate/", json=payload)
print("Status code:", resp.status_code)
print("Response text:", resp.text)
if resp.status_code == 200:
    print(resp.json())
else:
    print("API call failed.")