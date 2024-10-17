from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType

from . import DOMAIN, GroheDataUpdateCoordinator

# Configuration for binary sensors
BINARY_SENSOR_CONFIG = {
    "Filter": {"key": "filter_empty", "device_class": "problem"},
    "CO2": {"key": "co2_empty", "device_class": "problem"},
}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Grohe Blue binary sensors based on a config entry."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for appliance_id, coordinator in coordinators.items():
        for name, config in BINARY_SENSOR_CONFIG.items():
            entities.append(GroheBinarySensor(coordinator, entry.entry_id, name, config, appliance_id))

    async_add_entities(entities)

class GroheBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Grohe Blue binary sensor for a specific device."""

    def __init__(self, coordinator: GroheDataUpdateCoordinator, entry_id: str, name: str, config: dict, appliance_id: str):
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{appliance_id}_{config['key']}"
        self._attr_device_class = config["device_class"]
        self._config = config
        self._appliance_id = appliance_id

    @property
    def is_on(self):
        """Return the state of the sensor (True if problem detected)."""
        return self.coordinator.data.get(self._config["key"], False)

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
