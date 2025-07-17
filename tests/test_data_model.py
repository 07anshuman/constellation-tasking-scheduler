import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data_model import DataModel

def test_data_model():
    model = DataModel(capacity_mb=500, downlink_rate_mbps=8)

    print("💾 Initial stored:", model.stored_data, "MB")

    # Try storing 3 images
    for i in range(3):
        success = model.store_image(size_mb=50)
        print(f"📸 Storing image {i+1}: {'Success' if success else 'Failed'} — Total:", model.stored_data, "MB")

    # Simulate a 2-minute downlink
    downlinked = model.downlink(dt_minutes=2)
    print("📡 Downlinked:", downlinked, "MB — Remaining:", model.stored_data, "MB")

    # Try to store a big image that won't fit
    success = model.store_image(size_mb=450)
    print("🛑 Try storing 450MB image:", "Success" if success else "Failed")

    print("💾 Fill level:", model.get_fill_level(), "%")

if __name__ == "__main__":
    test_data_model()
