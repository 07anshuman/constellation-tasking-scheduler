from core.scheduler import run_simulation
from utils.config_loader import load_configs

start_time, duration, timestep, satellites, ground_stations, targets = load_configs(
    scenario_path="scenario.yaml", targets_path="targets.yaml"
)
scenario = {
    "start_time": start_time,
    "duration_minutes": duration.total_seconds() / 60,
    "timestep_sec": timestep,
    "satellites": satellites,
    "ground_stations": ground_stations,
}
run_simulation(scenario, targets, "outputs/manual_test.csv")