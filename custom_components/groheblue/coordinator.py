"""Responsible for updating the sensor values in a specified time interval."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta

from groheblue import GroheClient
import logging

_LOGGER = logging.getLogger(__name__)


class GroheDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Grohe data from a single endpoint for a specific device."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: GroheClient,
        appliance_id: str,
        serial_number: str,
        polling_interval: int,
    ):
        """Initialize the coordinator for a specific device."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Grohe Blue Data Coordinator {appliance_id}",
            update_interval=timedelta(seconds=polling_interval),
        )

        self.client = client
        self.appliance_id = appliance_id
        self.serial_number = serial_number  # Store serial number in coordinator

    async def _async_update_data(self):
        """Fetch data for this specific appliance ID from GroheClient."""
        devices = await self.client.get_devices()

        old_device_data = next(
            device for device in devices if device.appliance_id == self.appliance_id
        )

        device_data = await self.client.get_current_measurement(old_device_data)

        return {
            "serial_number": self.serial_number,
            "remaining_co2": device_data.data_latest.remaining_co2,
            "remaining_filter": device_data.data_latest.remaining_filter,
            "remaining_co2_liters": device_data.data_latest.remaining_co2_liters,
            "remaining_filter_liters": device_data.data_latest.remaining_filter_liters,
            "cleaning_count": device_data.data_latest.cleaning_count,
            "date_of_cleaning": device_data.data_latest.date_of_cleaning,
            "date_of_co2_replacement": device_data.data_latest.date_of_co2_replacement,
            "date_of_filter_replacement": device_data.data_latest.date_of_filter_replacement,
            "power_cut_count": device_data.data_latest.power_cut_count,
            "pump_count": device_data.data_latest.pump_count,
            "pump_running_time": device_data.data_latest.pump_running_time,
            "operating_time": device_data.data_latest.operating_time,
            "water_running_time_still": device_data.data_latest.water_running_time_still,
            "water_running_time_carbonated": device_data.data_latest.water_running_time_carbonated,
            "water_running_time_medium": device_data.data_latest.water_running_time_medium,
            "System_error_bitfield": device_data.state.System_error_bitfield,
            "filter_empty": device_data.state.filter_empty,
            "co2_empty": device_data.state.co2_empty,
            "time_since_last_withdrawal": device_data.data_latest.time_since_last_withdrawal,
            "timestamp": device_data.data_latest.timestamp,
            "filter_change_count": device_data.data_latest.filter_change_count,
            "filter_type": device_data.params.filter_type,
        }

    def update_polling_interval(self, new_interval: int):
        """Update the polling interval and reschedule updates."""
        self.update_interval = timedelta(seconds=new_interval)
        self.async_update_listeners()
