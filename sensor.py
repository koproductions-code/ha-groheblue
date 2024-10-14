from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import GroheDataUpdateCoordinator, DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Grohe Blue sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([GroheRemainingCO2Sensor(coordinator, entry.entry_id)])

class GroheRemainingCO2Sensor(CoordinatorEntity, SensorEntity):
    """Representation of the Grohe Blue Remaining CO2 sensor."""

    def __init__(self, coordinator: GroheDataUpdateCoordinator, entry_id: str):
        super().__init__(coordinator)
        self._attr_name = "Remaining CO2 Level"
        self._attr_unit_of_measurement = "percent"
        self._attr_unique_id = f"{entry_id}_remaining_co2"
        self._entry_id = entry_id

    @property
    def native_value(self):
        """Return the current remaining CO2 level."""
        return self.coordinator.data.get("remaining_co2")

    @property
    def device_info(self):
        """Return device info to link the sensor to the main device."""
        return {
            "identifiers": {(DOMAIN, "1e7f471f-3b1e-40e5-a665-c1aaa898eae9")},
            "name": "My GROHE Blue Home",
            "manufacturer": "Grohe",
            "model": "Blue Home",
            "entry_type": "service",
        }
