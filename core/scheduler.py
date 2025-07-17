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
    scenario_config,
    targets,
    output_csv="outputs/energy_data_log.csv"
):
    from skyfield.api import load, EarthSatellite, wgs84
    from datetime import datetime, timedelta, timezone

    ts = load.timescale()
    eph = load('de421.bsp')

    satellites = scenario_config['satellites']
    duration_min = scenario_config['duration_minutes']
    timestep_sec = scenario_config['timestep_sec']
    ground_stations = scenario_config.get('ground_stations', [])
    min_elev = scenario_config.get('min_elevation_deg', 10)

    if not ground_stations:
        raise ValueError("No ground stations defined in scenario.")

    ground = wgs84.latlon(ground_stations[0]['lat'], ground_stations[0]['lon'])

    # Prepare output
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = [
            'timestamp', 'satellite', 'action', 'in_sunlight',
            'over_target', 'over_ground', 'energy_wh', 'battery_pct',
            'data_mb', 'storage_pct'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        start_time = datetime.utcnow().replace(tzinfo=timezone.utc)

        for sat_cfg in satellites:
            name = sat_cfg['name']
            tle = sat_cfg['tle']
            sat = EarthSatellite(tle[0], tle[1], name, ts)
            energy_model = EnergyModel(capacity_wh=sat_cfg['energy_capacity_wh'])
            data_model = DataModel(
                capacity_mb=sat_cfg.get("storage_capacity_mb", 500.0),
                downlink_rate_mbps=sat_cfg.get("downlink_bandwidth_mbps", 10.0)
            )
            time = start_time
            for _ in range(duration_min):
                t = ts.utc(time)
                sunlit = sat.at(t).is_sunlit(eph)
                over_target = any(
                    is_visible(sat, wgs84.latlon(tgt['lat'], tgt['lon']), t, min_elev)
                    for tgt in targets
                )
                over_ground = is_visible(sat, ground, t, min_elev)

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
                    'satellite': name,
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
