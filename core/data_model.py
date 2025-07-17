import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class DataModel:
    def __init__(self, capacity_mb: float = 500.0, downlink_rate_mbps: float = 10.0, initial_mb: float = 0.0):
        """
        Initialize the data storage model.

        Args:
            capacity_mb (float): Max onboard storage in MB.
            downlink_rate_mbps (float): Downlink bandwidth in Mbps.
            initial_mb (float): Initial onboard data in MB.
        """
        self.capacity = capacity_mb
        self.downlink_rate_mbps = downlink_rate_mbps
        self.stored_data = min(initial_mb, capacity_mb)  # Avoid overflow at start

    def store_image(self, size_mb: float = 50.0) -> bool:
        """
        Attempt to store image data onboard.

        Args:
            size_mb (float): Size of the image to store.

        Returns:
            bool: True if stored successfully, False if not enough space.
        """
        if self.stored_data + size_mb <= self.capacity:
            self.stored_data += size_mb
            return True
        return False

    def downlink(self, dt_minutes: float) -> float:
        """
        Simulate data downlink over a given time window.

        Args:
            dt_minutes (float): Duration of downlink session in minutes.

        Returns:
            float: Amount of data downlinked in MB.
        """
        downlink_capacity = (self.downlink_rate_mbps / 8.0) * 60.0 * dt_minutes  # Mbps to MB
        downlinked = min(self.stored_data, downlink_capacity)
        self.stored_data -= downlinked
        return downlinked

    def get_fill_level(self) -> float:
        """
        Get current storage fill level.

        Returns:
            float: Percentage of storage used.
        """
        return (self.stored_data / self.capacity) * 100.0 if self.capacity > 0 else 0.0
