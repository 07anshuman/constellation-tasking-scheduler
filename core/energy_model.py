import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class EnergyModel:
    def __init__(self, capacity_wh=100.0, charge_rate_wh_per_min=2.0, discharge_rate_wh_per_min=5.0):
        """
        Initialize the energy model.

        Args:
            capacity_wh (float): Max energy capacity in watt-hours.
            charge_rate_wh_per_min (float): Rate of charging when in sunlight.
            discharge_rate_wh_per_min (float): Rate of discharging during operations.
        """
        self.capacity = capacity_wh
        self.charge_rate = charge_rate_wh_per_min
        self.discharge_rate = discharge_rate_wh_per_min
        self.energy = capacity_wh / 2  # Start at 50% SOC

    def step(self, in_sunlight: bool, action: str, dt_minutes: float) -> float:
        """
        Simulate a time step of battery behavior.

        Args:
            in_sunlight (bool): Whether the satellite is in sunlight.
            action (str): 'image', 'downlink', or 'idle'.
            dt_minutes (float): Time interval in minutes.

        Returns:
            float: New energy level (wh).
        """
        if in_sunlight:
            self.energy = min(self.capacity, self.energy + self.charge_rate * dt_minutes)

        if action in ['image', 'downlink']:
            self.energy = max(0.0, self.energy - self.discharge_rate * dt_minutes)

        return self.energy

    def can_perform(self, required_energy: float) -> bool:
        """
        Check if the current energy is enough for an action.

        Args:
            required_energy (float): Required energy in Wh.

        Returns:
            bool: True if action is feasible.
        """
        return self.energy >= required_energy

    def get_soc(self) -> float:
        """
        Get state of charge as a percentage.
        """
        return (self.energy / self.capacity) * 100.0
