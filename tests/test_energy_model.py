import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.energy_model import EnergyModel

def test_energy_model():
    model = EnergyModel(capacity_wh=100, charge_rate_wh_per_min=2, discharge_rate_wh_per_min=5)

    print("🔋 Starting energy:", model.energy, "Wh")

    # Simulate 10 min in sunlight with no action
    for _ in range(10):
        model.step(in_sunlight=True, action='idle', dt_minutes=1)

    print("☀️ After 10 min sunlight (idle):", model.energy, "Wh")

    # Simulate 5 min of imaging (should discharge)
    for _ in range(5):
        model.step(in_sunlight=False, action='image', dt_minutes=1)

    print("📸 After 5 min imaging (dark):", model.energy, "Wh")

    # Simulate 10 min idle in dark
    for _ in range(10):
        model.step(in_sunlight=False, action='idle', dt_minutes=1)

    print("🌑 After 10 min idle (dark):", model.energy, "Wh")

    # Check if we have enough energy for a future task needing 20Wh
    print("✅ Can perform task needing 20Wh?", model.can_perform(20))
    print("🔋 SOC:", model.get_soc(), "%")

if __name__ == "__main__":
    test_energy_model()
