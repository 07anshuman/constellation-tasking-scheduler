import argparse
import os
from core.scheduler import run_simulation
from utils.config_loader import load_configs

def main():
    parser = argparse.ArgumentParser(description="Constellation Scheduler")
    parser.add_argument('--targets', default='targets.yaml', help='Path to targets YAML file')
    parser.add_argument('--scenario', default='scenario.yaml', help='Path to scenario YAML file')
    args = parser.parse_args()
    print(f"Using scenario file: {args.scenario}")
    # Load unified configuration
    start_time, duration, timestep, satellites, ground_stations, targets = load_configs(
        scenario_path=args.scenario,
        targets_path=args.targets
    )
    print("[DEBUG] Sample target:", targets[0])
    # Build scenario dict
    scenario = {
        "start_time": start_time,
        "duration_minutes": duration.total_seconds() / 60,
        "timestep_sec": timestep,
        "satellites": satellites,
        "ground_stations": ground_stations,
    }

    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/simulation_log.csv"

    print("▶ Starting simulation...")
    run_simulation(scenario, targets, output_path)
    print(f"✅ Simulation complete. Log written to {output_path}")

if __name__ == "__main__":
    main()
