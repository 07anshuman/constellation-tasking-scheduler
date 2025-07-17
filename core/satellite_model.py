from skyfield.api import EarthSatellite, wgs84, load
from core.energy_model import EnergyModel
from core.data_model import DataModel

class SatelliteModel:
    def __init__(self, sat_config, ts):
        self.id = sat_config['name']
        self.tle = sat_config['tle']
        self.sat = EarthSatellite(self.tle[0], self.tle[1], self.id, ts)

        # Initialize energy model with realistic config
        self.energy = EnergyModel(
            capacity_wh=sat_config["battery_wh"],
            initial_wh=sat_config["initial_battery_wh"],
            charge_rate_w=sat_config["charge_rate_w"],
            imaging_power_w=sat_config["imaging_power_w"],
            downlink_power_w=sat_config["downlink_power_w"],
            idle_power_w=sat_config["idle_power_w"]
        )

        # Initialize data model
        self.data = DataModel(
            capacity_mb=sat_config["storage_capacity_mb"]
        )

        self.downlink_mbps = sat_config["downlink_bandwidth_mbps"]

    def propagate(self, t):
        return self.sat.at(t)

    def is_sunlit(self, eph, t):
        return self.sat.at(t).is_sunlit(eph)

    def is_visible(self, target, t, min_elev_deg):
        difference = self.sat - target
        topocentric = difference.at(t)
        alt, _, _ = topocentric.altaz()
        return alt.degrees > min_elev_deg
