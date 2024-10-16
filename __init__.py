"""__init__.py file for the Grohe Blue integration."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr

from .GroheClient.base import GroheClient
from .GroheClient.tap_controller import get_dashboard_data, execute_tap_command

from .coordinator import GroheDataUpdateCoordinator

DOMAIN = "groheblue"
_LOGGER = logging.getLogger(__name__)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["sensor", "binary_sensor"]
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload a config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_reload_integration(call, hass):
    """Handle the reload service call."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        await async_reload_entry(hass, entry)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Grohe Blue component."""
    hass.services.async_register(
        DOMAIN, "reload", lambda call: async_reload_integration(call, hass)
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Grohe Blue component with multiple devices and serial numbers."""

    email = entry.data.get("email")
    password = entry.data.get("password")

    client = GroheClient(email=email, password=password)
    await client._initialize_tokens()

    data = await get_dashboard_data(await client.get_access_token())
    devices = data["locations"][0]["rooms"][0]["appliances"]

    coordinators = {}

    for device in devices:
        appliance_id = device["appliance_id"]
        name = device["name"]
        serial_number = device["serial_number"]

        coordinator = GroheDataUpdateCoordinator(
            hass, client, appliance_id, serial_number
        )
        await coordinator.async_config_entry_first_refresh()
        coordinators[appliance_id] = coordinator

        device_registry = dr.async_get(hass)
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, appliance_id)},
            name=name,
            manufacturer="Grohe",
            model="Blue Home",
            sw_version=device.get("version"),
            hw_version=serial_number,
        )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "binary_sensor"]
    )

    async def handle_tap_water(call):
        tap_type = call.data.get("type")
        amount = call.data.get("amount")

        await execute_tap_command(tap_type, amount, client)

    hass.services.async_register("groheblue", "tap_water", handle_tap_water)

    return True
