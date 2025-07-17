import argparse
import os
from core.scheduler import run_simulation  # FIXED SPELLING
from utils.config_loader import load_targets, load_scenario


def main():
    
    parser = argparse.ArgumentParser(description="Constellation Scheduler")
    parser.add_argument('--targets', default='targets.yaml', help='Path to targets YAML file')
    parser.add_argument('--scenario', default='scenario.yaml', help='Path to scenario YAML file')
    args = parser.parse_args()

    targets = load_targets(args.targets)
    scenario = load_scenario(args.scenario)
    satellites = scenario["satellites"]
    ground_stations = scenario["ground_stations"]

    for sat in satellites:
        tle_lines = sat["tle"]
        sat_name = sat["name"]

        if len(tle_lines) != 2:
            raise ValueError(f"Satellite {sat_name} has invalid TLE: {tle_lines}")

        for target in targets:
            for gs in ground_stations:
                print(f"▶ Simulating {sat_name} over {target['name']} using GS {gs['name']}")
                
                os.makedirs("outputs", exist_ok=True)

                output_path = f"outputs/log_{target['name']}_{gs['name']}_{sat_name}.csv"

                run_simulation(scenario, targets, output_path)



if __name__ == "__main__":
    main()
