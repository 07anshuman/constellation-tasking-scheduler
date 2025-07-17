import yaml
from datetime import datetime, timezone


def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def load_scenario(path="scenario.yaml"):
    data = load_yaml(path)
    
    # Parse time
    start_time = datetime.fromisoformat(data["start_time"].replace("Z", "+00:00"))
    
    return {
        "name": data["scenario_name"],
        "start_time": start_time,
        "duration_minutes": data["duration_minutes"],
        "timestep_sec": data.get("timestep_sec", 60),
        "weather_model": data.get("weather_model", "clear_only"),
        "min_elevation_deg": data.get("min_elevation_deg", 15),
        "imaging_mode": data.get("imaging_mode", "priority"),
        "satellites": data["satellites"],
        "ground_stations": data.get("ground_stations", [
            {"name": "DefaultGS", "lat": 0.0, "lon": 0.0}
        ])
    }



def load_targets(path="targets.yaml"):
    return load_yaml(path)
