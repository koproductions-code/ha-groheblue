"""Responsible for updating the sensor values in a specified time interval."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import HomeAssistantError
from datetime import timedelta

from .GroheClient.base import GroheClient
from .GroheClient.tap_controller import get_dashboard_data
from . import _LOGGER


class GroheDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Grohe data from a single endpoint for a specific device."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: GroheClient,
        appliance_id: str,
        serial_number: str,
    ):
        """Initialize the coordinator for a specific device."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Grohe Blue Data Coordinator {appliance_id}",
            update_interval=timedelta(minutes=5),
        )
        self.client = client
        self.appliance_id = appliance_id
        self.serial_number = serial_number  # Store serial number in coordinator

    async def _async_update_data(self):
        """Fetch data for this specific appliance ID from GroheClient."""
        data = await get_dashboard_data(await self.client.get_access_token())
        if "locations" not in data:
            raise HomeAssistantError(f"Error fetching the data {data}")

        device_data = next(
            device
            for device in data["locations"][0]["rooms"][0]["appliances"]
            if device["appliance_id"] == self.appliance_id
        )
        measurement_data = device_data["data_latest"]["measurement"]
        state_data = device_data["state"]

        return {
            "serial_number": self.serial_number,
            "remaining_co2": measurement_data["remaining_co2"],
            "remaining_filter": measurement_data["remaining_filter"],
            "remaining_co2_liters": measurement_data["remaining_co2_liters"],
            "remaining_filter_liters": measurement_data["remaining_filter_liters"],
            "cleaning_count": measurement_data["cleaning_count"],
            "date_of_cleaning": measurement_data["date_of_cleaning"],
            "date_of_co2_replacement": measurement_data["date_of_co2_replacement"],
            "date_of_filter_replacement": measurement_data[
                "date_of_filter_replacement"
            ],
            "power_cut_count": measurement_data["power_cut_count"],
            "pump_count": measurement_data["pump_count"],
            "pump_running_time": measurement_data["pump_running_time"],
            "operating_time": measurement_data["operating_time"],
            "water_running_time_still": measurement_data["water_running_time_still"],
            "water_running_time_carbonated": measurement_data[
                "water_running_time_carbonated"
            ],
            "water_running_time_medium": measurement_data["water_running_time_medium"],
            "System_error_bitfield": state_data["System_error_bitfield"],
            "filter_empty": state_data["filter_empty"],
            "co2_empty": state_data["co2_empty"],
        }
