import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.energy_model import EnergyModel

def test_energy_model():
    # Instantiate model with example values
    model = EnergyModel(
        capacity_wh=100.0,
        initial_wh=50.0,
        charge_rate_w=20.0,         # charging at 20W in sunlight
        imaging_power_w=15.0,       # imaging consumes 15W
        downlink_power_w=10.0,      # downlink consumes 10W
        idle_power_w=2.0            # idle still drains 2W
    )

    print(f"🔋 Initial energy: {model.energy:.2f} Wh")

    # 10 min in sunlight, idle
    for _ in range(10):
        model.step(in_sunlight=True, action='idle', dt_minutes=1)
    print(f"☀️ After 10 min sunlight + idle: {model.energy:.2f} Wh")

    # 5 min in dark, imaging
    for _ in range(5):
        model.step(in_sunlight=False, action='image', dt_minutes=1)
    print(f"📸 After 5 min imaging (dark): {model.energy:.2f} Wh")

    # 3 min in sunlight, downlink
    for _ in range(3):
        model.step(in_sunlight=True, action='downlink', dt_minutes=1)
    print(f"📡 After 3 min downlink (sunlight): {model.energy:.2f} Wh")

    # 10 min idle in dark
    for _ in range(10):
        model.step(in_sunlight=False, action='idle', dt_minutes=1)
    print(f"🌑 After 10 min idle (dark): {model.energy:.2f} Wh")

    # Can we perform an imaging task that needs 5Wh?
    print("✅ Can perform 5Wh imaging task?", model.can_perform(5.0))

    # Can we perform a 60Wh long downlink?
    print("❌ Can perform 60Wh downlink task?", model.can_perform(60.0))

    print(f"🔋 Final SOC: {model.get_soc():.2f}%")

if __name__ == "__main__":
    test_energy_model()
