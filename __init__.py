from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers import device_registry as dr
from homeassistant.exceptions import HomeAssistantError
from datetime import timedelta
import logging

from .GroheClient.base import GroheClient
from .GroheClient.tap_controller import get_dashboard_data, execute_tap_command

DOMAIN = "groheblue"
_LOGGER = logging.getLogger(__name__)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload a config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

async def async_reload_integration(call):
    """Handle the reload service call."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        await async_reload_entry(hass, entry)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Grohe Blue component."""
    # Register the reload service
    hass.services.async_register(DOMAIN, "reload", async_reload_integration)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Grohe Blue component with multiple devices and serial numbers."""

    email = entry.data.get("email")
    password = entry.data.get("password")

    client = GroheClient(email=email, password=password)
    await client._initialize_tokens()

    # Fetch data once to identify all devices and their serial numbers
    data = await get_dashboard_data(await client.get_access_token())
    devices = data['locations'][0]['rooms'][0]['appliances']

    coordinators = {}

    for device in devices:
        appliance_id = device['appliance_id']
        name = device['name']
        serial_number = device['serial_number']

        # Create a coordinator for each device, passing the serial number to be stored in data
        coordinator = GroheDataUpdateCoordinator(hass, client, appliance_id, serial_number)
        await coordinator.async_config_entry_first_refresh()
        coordinators[appliance_id] = coordinator

        # Register the device in Home Assistant's device registry with the serial number
        device_registry = dr.async_get(hass)
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, appliance_id)},
            name=name,
            manufacturer="Grohe",
            model="Blue Home",
            sw_version=device.get("version"),  # Optional: include software version if available
            hw_version=serial_number,  # Register the serial number as hardware version
        )

    # Store the coordinators in hass.data for access by entities
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinators

    # Forward the setup of the sensor platform to Home Assistant
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])


    # Register Tap Water Service
    async def handle_tap_water(call):
        tap_type = call.data.get('type')
        amount = call.data.get('amount')

        await execute_tap_command(tap_type, amount, client)
    
    hass.services.async_register('groheblue', 'tap_water', handle_tap_water)

    return True

class GroheDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Grohe data from a single endpoint for a specific device."""

    def __init__(self, hass: HomeAssistant, client: GroheClient, appliance_id: str, serial_number: str):
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
        if ("locations" not in data):
            raise HomeAssistantError(f"Error fetching the data {data}")

        device_data = next(
            device for device in data['locations'][0]['rooms'][0]['appliances']
            if device['appliance_id'] == self.appliance_id
        )
        measurement_data = device_data['data_latest']['measurement']
        state_data = device_data['state']

        return {
            "serial_number": self.serial_number,  # Include serial number in returned data
            "remaining_co2": measurement_data['remaining_co2'],
            "remaining_filter": measurement_data['remaining_filter'],
            "remaining_co2_liters": measurement_data['remaining_co2_liters'],
            "remaining_filter_liters": measurement_data['remaining_filter_liters'],
            "cleaning_count": measurement_data['cleaning_count'],
            "date_of_cleaning": measurement_data['date_of_cleaning'],
            "date_of_co2_replacement": measurement_data['date_of_co2_replacement'],
            "date_of_filter_replacement": measurement_data['date_of_filter_replacement'],
            "power_cut_count": measurement_data['power_cut_count'],
            "pump_count": measurement_data['pump_count'],
            "pump_running_time": measurement_data['pump_running_time'],
            "operating_time": measurement_data['operating_time'],
            "water_running_time_still": measurement_data['water_running_time_still'],
            "water_running_time_carbonated": measurement_data['water_running_time_carbonated'],
            "water_running_time_medium": measurement_data['water_running_time_medium'],
            "System_error_bitfield": state_data['System_error_bitfield'],
            "filter_empty": state_data['filter_empty'],
            "co2_empty": state_data['co2_empty']
        }
