# utils/config_loader.py

import yaml
from pathlib import Path
from datetime import datetime, timedelta

def load_configs(scenario_path: str, targets_path: str):
    with open(scenario_path, 'r') as f:
        scenario = yaml.safe_load(f)

    with open(targets_path, 'r') as f:
        targets = yaml.safe_load(f)

    start_time = datetime.fromisoformat(scenario['simulation']['start_time'].replace("Z", "+00:00"))
    duration = timedelta(minutes=scenario['simulation']['duration_minutes'])
    timestep = scenario['simulation']['timestep_seconds']

    satellites = scenario['satellites']
    ground_stations = scenario.get('ground_stations', [])

    return start_time, duration, timestep, satellites, ground_stations, targets
