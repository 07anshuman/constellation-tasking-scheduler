import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class DataModel:
    def __init__(self, capacity_mb=500.0, downlink_rate_mbps=10.0):
        """
        Initialize the data storage model.

        Args:
            capacity_mb (float): Max onboard storage in MB.
            downlink_rate_mbps (float): Downlink bandwidth in Mbps.
        """
        self.capacity = capacity_mb
        self.downlink_rate_mbps = downlink_rate_mbps
        self.stored_data = 0.0

    def store_image(self, size_mb: float = 50.0) -> bool:
        """
        Try to store image data onboard.

        Args:
            size_mb (float): Size of the image to store.

        Returns:
            bool: True if image stored, False if not enough space.
        """
        if self.stored_data + size_mb <= self.capacity:
            self.stored_data += size_mb
            return True
        return False

    def downlink(self, dt_minutes: float) -> float:
        """
        Simulate data downlink over a given duration.

        Args:
            dt_minutes (float): Duration of downlink session in minutes.

        Returns:
            float: Amount of data downlinked in MB.
        """
        downlink_capacity = (self.downlink_rate_mbps / 8) * 60 * dt_minutes  # MB = Mbps / 8 * 60 * min
        downlinked = min(self.stored_data, downlink_capacity)
        self.stored_data -= downlinked
        return downlinked

    def get_fill_level(self) -> float:
        """
        Get percentage of storage used.
        """
        return (self.stored_data / self.capacity) * 100.0
