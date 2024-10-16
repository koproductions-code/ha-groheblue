from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType

from . import DOMAIN, GroheDataUpdateCoordinator

# Configuration map for sensors
SENSOR_CONFIG = {
    "Remaining CO2": {"key": "remaining_co2", "unit": "%"},
    "Remaining Filter": {"key": "remaining_filter", "unit": "%"},
    "Remaining CO2 Liters": {"key": "remaining_co2_liters", "unit": "L"},
    "Remaining Filter Liters": {"key": "remaining_filter_liters", "unit": "L"},
    "Cleaning Count": {"key": "cleaning_count", "unit": ""},
    "Date of Last Cleaning": {"key": "date_of_cleaning", "unit": "date"},
    "Date of Last CO2 Replacement": {"key": "date_of_co2_replacement", "unit": "date"},
    "Date of Last Filter Replacement": {"key": "date_of_filter_replacement", "unit": "date"},
    "Power Cut Count": {"key": "power_cut_count", "unit": ""},
    "Pump Count": {"key": "pump_count", "unit": ""},
    "Pump Running Time": {"key": "pump_running_time", "unit": "min"},
    "Operating Time": {"key": "operating_time", "unit": "min"},
    "Water Running Time (Still)": {"key": "water_running_time_still", "unit": "s"},
    "Water Running Time (Carbonated)": {"key": "water_running_time_carbonated", "unit": "s"},
    "Water Running Time (Medium)": {"key": "water_running_time_medium", "unit": "s"},
    "System Error Bitfield": {"key": "System_error_bitfield", "unit": ""},
}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Grohe Blue sensors based on a config entry, with support for multiple devices."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for appliance_id, coordinator in coordinators.items():
        for name, config in SENSOR_CONFIG.items():
            entities.append(GroheSensor(coordinator, entry.entry_id, name, config, appliance_id))

    async_add_entities(entities)

class GroheSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Grohe Blue sensor for a specific device."""

    def __init__(self, coordinator: GroheDataUpdateCoordinator, entry_id: str, name: str, config: dict, appliance_id: str):
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{appliance_id}_{config['key']}"
        #self._attr_unit_of_measurement = config["unit"]
        if config["unit"] != "date":
            self._attr_native_unit_of_measurement = config["unit"]
        else:
            self._attr_unit_of_measurement = config["unit"]

        self._config = config
        self._appliance_id = appliance_id

    @property
    def native_value(self):
        """Return the current value for the sensor."""
        return self.coordinator.data.get(self._config["key"])

    @property
    def device_info(self):
        """Return device info to link the sensor to the correct appliance."""
        serial_number = self.coordinator.data.get("serial_number", "Unknown")
        return {
            "identifiers": {(DOMAIN, self._appliance_id)},
            "name": f"My GROHE Blue Home {self._appliance_id}",
            "manufacturer": "Grohe",
            "model": "Blue Home",
            "hw_version": serial_number,  # Include serial number here
            "entry_type": DeviceEntryType.SERVICE,
        }
