import math
from skyfield.api import load, EarthSatellite, wgs84
from datetime import datetime, timedelta
import numpy as np
import csv
import os
import json
from core.energy_model import EnergyModel
from core.data_model import DataModel
from typing import Dict, Optional

def is_visible(sat, location, time, min_elev_deg):
    difference = sat - location
    topocentric = difference.at(time)
    alt, _, _ = topocentric.altaz()
    return alt.degrees > min_elev_deg

def vector_to_target(sat, lat, lon, t):
    sat_pos = np.array(sat.at(t).position.km)
    tgt_pos = np.array(wgs84.latlon(lat, lon).at(t).position.km)
    vec = tgt_pos - sat_pos
    return vec / np.linalg.norm(vec)

def angle_between(vec1, vec2):
    dot = np.clip(np.dot(vec1, vec2), -1.0, 1.0)
    return math.degrees(math.acos(dot))

def lookahead_energy_ok(energy_model, current_energy, sunlit, action, action_minutes, min_reserve_wh=10.0):
    """
    Simulate energy after performing the action, then simulate idle (in dark) until next sunlight.
    Returns True if energy will stay above min_reserve_wh.
    """
    # Simulate the action
    temp_energy = current_energy
    dt_hours = action_minutes / 60.0

    # Subtract energy for the action
    if action == "image":
        temp_energy -= energy_model.imaging_power_w * dt_hours
    elif action == "downlink":
        temp_energy -= energy_model.downlink_power_w * dt_hours
    elif action == "idle":
        temp_energy -= energy_model.idle_power_w * dt_hours

    # Simulate idle in dark for a lookahead period (e.g., 10 min)
    lookahead_minutes = 10
    temp_energy -= energy_model.idle_power_w * (lookahead_minutes / 60.0)

    # Optionally, add charging if sunlit
    if sunlit:
        temp_energy += energy_model.charge_rate_w * (lookahead_minutes / 60.0)
        temp_energy = min(temp_energy, energy_model.capacity)

    return temp_energy >= min_reserve_wh

def run_simulation(scenario, targets, output_path):
    ts = load.timescale()
    eph = load('de421.bsp')

    start_time = scenario['start_time']
    if isinstance(start_time, str):
        # Accept both with and without timezone
        try:
            start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        except Exception:
            # fallback: try parsing without timezone
            start_time = datetime.fromisoformat(start_time)    
    duration_min = scenario['duration_minutes']
    timestep_sec = scenario['timestep_sec']
    steps = int(duration_min * 60 / timestep_sec)

    min_elev = scenario.get('min_elevation_deg', 10)
    max_slew_deg = scenario.get('max_slew_angle_deg', 20)
    ground_stations = scenario.get('ground_stations', [])

    sats = []
    for sat_cfg in scenario['satellites']:
        sat = EarthSatellite(sat_cfg['tle'][0], sat_cfg['tle'][1], sat_cfg['name'], ts)
        sats.append({
            "name": sat_cfg["name"],
            "sat": sat,
            "energy": EnergyModel(
                capacity_wh=sat_cfg["battery_wh"],
                initial_wh=sat_cfg.get("initial_battery_wh", sat_cfg["battery_wh"]),
                charge_rate_w=sat_cfg["charge_rate_w"],
                imaging_power_w=sat_cfg["imaging_power_w"],
                downlink_power_w=sat_cfg["downlink_power_w"],
                idle_power_w=sat_cfg["idle_power_w"]
            ),
            "data": DataModel(
                capacity_mb=sat_cfg["storage_capacity_mb"],
                downlink_rate_mbps=sat_cfg["downlink_bandwidth_mbps"],
                initial_mb=sat_cfg.get("initial_storage_mb", 0)
            ),
            "last_att_vec": None,
            "last_imaged": {tgt["name"]: None for tgt in targets}
        })

    last_imaged_global: Dict[str, Optional[datetime]] = {tgt["name"]: None for tgt in targets}

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    results = []
    with open(output_path, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "satellite", "action", "in_sunlight", "over_target", "over_ground",
            "energy_wh", "battery_pct", "data_mb", "storage_pct"
        ])
        writer.writeheader()

        for step in range(steps):
            sim_time = start_time + timedelta(seconds=step * timestep_sec)
            t = ts.utc(sim_time)

            for s in sats:
                sat = s["sat"]
                energy = s["energy"]
                data = s["data"]
                name = s["name"]
                sunlit = sat.at(t).is_sunlit(eph)

                # Visible targets with allowed slew
                eligible_targets = []
                for tgt in targets:
                    loc = wgs84.latlon(tgt['lat'], tgt['lon'])
                    if not is_visible(sat, loc, t, min_elev):
                        continue

                    revisit_td = timedelta(hours=tgt['revisit_hours'])
                    last = last_imaged_global[tgt['name']]
                    if last is not None and (sim_time - last) < revisit_td:
                        continue

                    vec = vector_to_target(sat, tgt['lat'], tgt['lon'], t)
                    if s["last_att_vec"] is not None:
                        slew_deg = angle_between(vec, s["last_att_vec"])
                        if slew_deg > max_slew_deg:
                            continue

                    eligible_targets.append((tgt, vec))

                best_target = None
                best_vec = None
                if eligible_targets:
                    eligible_targets.sort(key=lambda x: (-x[0]["priority"], last_imaged_global[x[0]["name"]] or datetime.min))
                    best_target, best_vec = eligible_targets[0]

                over_ground = any(
                    is_visible(sat, wgs84.latlon(gs['lat'], gs['lon']), t, min_elev)
                    for gs in ground_stations
                )

                action = "idle"

                if best_target:
                    mb = best_target['image_size_mb']
                    wh = best_target['image_energy_wh']

                    if (
                        energy.can_perform(wh)
                        and data.store_image(mb)
                        and lookahead_energy_ok(energy, energy.energy, sunlit, 'image', timestep_sec / 60)
                    ):
                        energy.step(sunlit, 'image', timestep_sec / 60)
                        s["last_att_vec"] = best_vec
                        s["last_imaged"][best_target["name"]] = sim_time
                        last_imaged_global[best_target["name"]] = sim_time
                        action = f"image:{best_target['name']}"
                    else:
                        # Detailed rejection reason
                        if not energy.can_perform(wh):
                            print(f"[{sat}] Skipped {best_target['name']} — insufficient energy "
                                f"({energy.energy:.2f}Wh < required {wh}Wh)")
                        elif not data.store_image(mb):
                            print(f"[{sat}] Skipped {best_target['name']} — insufficient storage for {mb}MB")
                        energy.step(sunlit, 'idle', timestep_sec / 60)

                elif over_ground:
                    downlink_wh = energy.downlink_power_w * timestep_sec / 3600  # W * sec / 3600 = Wh
                    if energy.can_perform(downlink_wh):
                        downlinked = data.downlink(timestep_sec / 60)
                        energy.step(sunlit, 'downlink', timestep_sec / 60)
                        action = 'downlink' if downlinked > 0 else 'idle'
                    else:
                        print(f"[{sat}] Skipped downlink — insufficient energy "
                            f"({energy.energy:.2f}Wh < required {downlink_wh:.2f}Wh)")
                        energy.step(sunlit, 'idle', timestep_sec / 60)

                else:
                    energy.step(sunlit, 'idle', timestep_sec / 60)

                row = {
                    "timestamp": sim_time.isoformat(),
                    "satellite": name,
                    "action": action,
                    "in_sunlight": bool(sunlit),
                    "over_target": bool(best_target),
                    "over_ground": bool(over_ground),
                    "energy_wh": float(round(energy.energy, 2)),
                    "battery_pct": float(round((energy.energy / energy.capacity) * 100, 1)),
                    "data_mb": float(round(data.stored_data, 2)),
                    "storage_pct": float(round((data.stored_data / data.capacity) * 100, 1)),
                }
                writer.writerow(row)
                results.append(row)

    json_path = output_path.replace('.csv', '.json')
    with open(json_path, 'w') as jf:
        json.dump(results, jf, indent=2)
    print(f"✅ JSON output saved to {json_path}")

    print(f"✅ Simulation complete. Log saved to {output_path}")
