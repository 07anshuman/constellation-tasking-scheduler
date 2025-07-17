import yaml
from datetime import datetime, timedelta


def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def normalize_ground_stations(gs_list):
    for gs in gs_list:
        if "latitude" in gs:
            gs["lat"] = gs.pop("latitude")
        if "longitude" in gs:
            gs["lon"] = gs.pop("longitude")
        if "altitude" in gs:
            gs["alt_m"] = gs.pop("altitude")
        elif "altitude_m" in gs:
            gs["alt_m"] = gs.pop("altitude_m")
        else:
            gs.setdefault("alt_m", 0.0)
    return gs_list


def load_scenario(path="scenario.yaml"):
    data = load_yaml(path)

    sim = data.get("simulation", {})

    start_time = datetime.fromisoformat(sim["start_time"].replace("Z", "+00:00"))

    return {
        "name": data.get("scenario_name", "UnnamedScenario"),
        "start_time": start_time,
        "duration_minutes": sim["duration_minutes"],
        "timestep_sec": sim.get("timestep_seconds", 60),
        "weather_model": sim.get("weather_model", "clear_only"),
        "min_elevation_deg": sim.get("min_elevation_deg", 15),
        "imaging_mode": sim.get("imaging_mode", "priority"),
        "satellites": data["satellites"],
        "ground_stations": normalize_ground_stations(data.get("ground_stations", [
            {"name": "DefaultGS", "lat": 0.0, "lon": 0.0, "alt_m": 0.0}
        ]))
    }


def load_targets(path="targets.yaml"):
    targets = load_yaml(path)
    return targets if isinstance(targets, list) else targets.get("targets", [])


def load_configs(scenario_path="scenario.yaml", targets_path="targets.yaml"):
    scenario = load_scenario(scenario_path)
    targets = load_targets(targets_path)

    start_time = scenario["start_time"]
    duration = timedelta(minutes=scenario["duration_minutes"])
    timestep = scenario["timestep_sec"]
    satellites = scenario["satellites"]
    ground_stations = scenario["ground_stations"]

    return start_time, duration, timestep, satellites, ground_stations, targets
