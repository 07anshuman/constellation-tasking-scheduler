from skyfield.api import load, EarthSatellite, wgs84
from datetime import datetime, timedelta, timezone
import csv
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.energy_model import EnergyModel
from core.data_model import DataModel

print("Running UPDATED SIMULATION SCRIPT")

def is_visible(sat, location, time, min_elev_deg=10.0):
    difference = sat - location
    topocentric = difference.at(time)
    alt, az, _ = topocentric.altaz()
    return alt.degrees > min_elev_deg

def run_simulation(
    tle_lines,
    target_latlon,
    ground_latlon,
    duration_min=90,
    timestep_sec=60,
    output_csv="outputs/energy_data_log.csv"
):
    ts = load.timescale()
    eph = load('de421.bsp')  # Load once here
    sat = EarthSatellite(tle_lines[0], tle_lines[1], "SAT", ts)

    target = wgs84.latlon(target_latlon[0], target_latlon[1])
    ground = wgs84.latlon(ground_latlon[0], ground_latlon[1])

    energy_model = EnergyModel()
    data_model = DataModel()

    start_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    time = start_time

    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = [
            'timestamp', 'action', 'in_sunlight',
            'over_target', 'over_ground',
            'energy_wh', 'battery_pct',
            'data_mb', 'storage_pct'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for _ in range(duration_min):
            t = ts.utc(time)

            sunlit = sat.at(t).is_sunlit(eph)
            over_target = is_visible(sat, target, t)
            over_ground = is_visible(sat, ground, t)

            action = 'idle'

            if over_target:
                if energy_model.can_perform(5) and data_model.store_image(50):
                    energy_model.step(sunlit, 'image', timestep_sec / 60)
                    action = 'image'
                else:
                    energy_model.step(sunlit, 'idle', timestep_sec / 60)

            elif over_ground:
                if energy_model.can_perform(5):
                    downlinked = data_model.downlink(timestep_sec / 60)
                    energy_model.step(sunlit, 'downlink', timestep_sec / 60)
                    action = 'downlink' if downlinked > 0 else 'idle'
                else:
                    energy_model.step(sunlit, 'idle', timestep_sec / 60)
            else:
                energy_model.step(sunlit, 'idle', timestep_sec / 60)

            writer.writerow({
                'timestamp': time.isoformat(),
                'action': action,
                'in_sunlight': sunlit,
                'over_target': over_target,
                'over_ground': over_ground,
                'energy_wh': round(energy_model.energy, 2),
                'battery_pct': round((energy_model.energy / energy_model.capacity) * 100, 1),
                'data_mb': round(data_model.stored_data, 2),
                'storage_pct': round((data_model.stored_data / data_model.capacity) * 100, 1),
            })

            time += timedelta(seconds=timestep_sec)

    print(f"✅ Simulation complete. Log saved to {output_csv}")
