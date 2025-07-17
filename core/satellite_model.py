from skyfield.api import EarthSatellite, wgs84, load
from core.energy_model import EnergyModel
from core.data_model import DataModel

class SatelliteModel:
    def __init__(self, sat_config, ts):
        self.id = sat_config['name']
        self.tle = sat_config['tle']
        self.sat = EarthSatellite(self.tle[0], self.tle[1], self.id, ts)

        self.energy = EnergyModel(capacity_wh=sat_config.get("energy_capacity_wh", 100))
        self.data = DataModel(capacity_mb=sat_config.get("storage_capacity_mb", 500))
        self.downlink_mbps = sat_config.get("downlink_bandwidth_mbps", 50)

    def propagate(self, t):
        return self.sat.at(t)

    def is_sunlit(self, eph, t):
        return self.sat.at(t).is_sunlit(eph)

    def is_visible(self, target, t, min_elev_deg):
        difference = self.sat - target
        topocentric = difference.at(t)
        alt, _, _ = topocentric.altaz()
        return alt.degrees > min_elev_deg
