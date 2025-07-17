import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class EnergyModel:
    def __init__(self,
                 capacity_wh: float,
                 initial_wh: float,
                 charge_rate_w: float,
                 imaging_power_w: float,
                 downlink_power_w: float,
                 idle_power_w: float):
        """
        Energy model with more realistic power draw and charging logic.
        """
        self.capacity = capacity_wh
        self.energy = min(initial_wh, capacity_wh)  # Clamp if initial > capacity
        self.charge_rate_w = charge_rate_w
        self.imaging_power_w = imaging_power_w
        self.downlink_power_w = downlink_power_w
        self.idle_power_w = idle_power_w

    def step(self, in_sunlight: bool, action: str, dt_minutes: float) -> float:
        dt_hours = dt_minutes / 60.0

        # Charge if in sunlight
        if in_sunlight:
            self.energy = min(self.capacity, self.energy + self.charge_rate_w * dt_hours)

        # Discharge based on action
        if action == "image":
            self.energy = max(0.0, self.energy - self.imaging_power_w * dt_hours)
        elif action == "downlink":
            self.energy = max(0.0, self.energy - self.downlink_power_w * dt_hours)
        elif action == "idle":
            self.energy = max(0.0, self.energy - self.idle_power_w * dt_hours)

        return self.energy

    def can_perform(self, required_energy: float) -> bool:
        return self.energy >= required_energy

    def get_soc(self) -> float:
        return (self.energy / self.capacity) * 100.0
