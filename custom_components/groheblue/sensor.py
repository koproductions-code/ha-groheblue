from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType

from . import DOMAIN, GroheDataUpdateCoordinator

from datetime import datetime

SENSOR_CONFIG = {
    "Remaining CO2": {
        "key": "remaining_co2",
        "unit": "%",
        "state_class": "measurement",
    },
    "Remaining Filter": {
        "key": "remaining_filter",
        "unit": "%",
        "device_class": "measurement",
    },
    "Remaining CO2 Liters": {
        "key": "remaining_co2_liters",
        "unit": "L",
        "device_class": "volume",
        "state_class": "total",
    },
    "Remaining Filter Liters": {
        "key": "remaining_filter_liters",
        "unit": "L",
        "device_class": "volume",
        "state_class": "total",
    },
    "Cleaning Count": {"key": "cleaning_count", "unit": "", "device_class": ""},
    "Date of Last Cleaning": {
        "key": "date_of_cleaning",
        "unit": "date",
        "device_class": "timestamp",
    },
    "Date of Last CO2 Replacement": {
        "key": "date_of_co2_replacement",
        "unit": "date",
        "device_class": "timestamp",
    },
    "Date of Last Filter Replacement": {
        "key": "date_of_filter_replacement",
        "unit": "date",
        "device_class": "timestamp",
    },
    "Power Cut Count": {
        "key": "power_cut_count",
        "unit": "",
        "device_class": "",
    },
    "Pump Count": {"key": "pump_count", "unit": "", "device_class": ""},
    "Pump Running Time": {
        "key": "pump_running_time",
        "unit": "min",
        "device_class": "duration",
        "state_class": "measurement",
    },
    "Operating Time": {
        "key": "operating_time",
        "unit": "min",
        "device_class": "duration",
        "state_class": "measurement",
    },
    "Water Running Time (Still)": {
        "key": "water_running_time_still",
        "unit": "min",
        "device_class": "duration",
        "state_class": "measurement",
    },
    "Water Running Time (Carbonated)": {
        "key": "water_running_time_carbonated",
        "unit": "min",
        "device_class": "duration",
        "state_class": "measurement",
    },
    "Water Running Time (Medium)": {
        "key": "water_running_time_medium",
        "unit": "min",
        "device_class": "duration",
        "state_class": "measurement",
    },
    "System Error Bitfield": {
        "key": "System_error_bitfield",
        "unit": "",
        "device_class": "",
    },
    "Time Since Last Withdrawal": {
        "key": "time_since_last_withdrawal",
        "unit": "min",
        "device_class": "duration",
        "state_class": "measurement",
    },
    "Timestamp": {"key": "timestamp", "unit": "date", "device_class": "timestamp"},
    "Filter Change Count": {
        "key": "filter_change_count",
        "unit": "",
        "device_class": "",
    },
    "Filter Type": {"key": "filter_type", "unit": "", "device_class": "enum"},
}

FILTER_TYPES = {
    1: "S_SIZE",
    2: "ACTIVE_CARBON",
    3: "ULTRA_SAFE",
    4: "MAGNESIUM_PLUS",
    5: "M_SIZE",
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up Grohe Blue sensors based on a config entry, with support for multiple devices."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for appliance_id, coordinator in coordinators.items():
        for name, config in SENSOR_CONFIG.items():
            entities.append(
                GroheSensor(coordinator, entry.entry_id, name, config, appliance_id)
            )

    async_add_entities(entities)


class GroheSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Grohe Blue sensor for a specific device."""

    def __init__(
        self,
        coordinator: GroheDataUpdateCoordinator,
        entry_id: str,
        name: str,
        config: dict,
        appliance_id: str,
    ):
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{appliance_id}_{config['key']}"

        if config["unit"] != "date":
            self._attr_native_unit_of_measurement = config["unit"]
        else:
            self._attr_unit_of_measurement = config["unit"]

        if "device_class" in config.keys() and config["device_class"]:
            self._attr_device_class = config["device_class"]

        if "state_class" in config.keys() and config["state_class"]:
            self._attr_state_class = config["state_class"]

        self._config = config
        self._appliance_id = appliance_id

    @property
    def native_value(self):
        """Return the current value for the sensor."""
        api_data = self.coordinator.data.get(self._config["key"])

        if self._config["unit"] == "date":
            if api_data:
                return datetime.fromisoformat(api_data)

        if self._config["key"] == "filter_type":
            if api_data:
                return FILTER_TYPES.get(api_data, api_data)

        return api_data

    @property
    def device_info(self):
        """Return device info to link the sensor to the correct appliance."""
        serial_number = self.coordinator.data.get("serial_number", "Unknown")
        return {
            "identifiers": {(DOMAIN, self._appliance_id)},
            "name": f"My GROHE Blue Home {self._appliance_id}",
            "manufacturer": "Grohe",
            "model": "Blue Home",
            "hw_version": serial_number,
            "entry_type": DeviceEntryType.SERVICE,
        }
