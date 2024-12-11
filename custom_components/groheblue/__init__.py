"""__init__.py file for the Grohe Blue integration."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr

from groheblue import GroheClient

from .coordinator import GroheDataUpdateCoordinator

DOMAIN = "groheblue"
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.ERROR)

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
    await client.login()

    devices = await client.get_devices()

    coordinators = {}

    for device in devices:
        appliance_id = device.appliance_id
        name = device.name
        serial_number = device.serial_number

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
            sw_version=device.version,
            hw_version=serial_number,
        )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor", "binary_sensor"]
    )

    async def handle_tap_water(call):
        target = call.data.get("device_id")[0]
        tap_type = call.data.get("type")
        amount = call.data.get("amount")

        entry = device_registry.async_get(target)
        grohe_id = next(iter(entry.identifiers))[1]

        devices = await client.get_devices()
        device = next(
            (device for device in devices if device.appliance_id == grohe_id), None
        )

        await client.dispense(device, tap_type, amount)
    
    async def handle_custom_command(call):
        target = call.data.get("device_id")[0]

        co2_status_reset = call.data.get("co2_status_reset", False)
        tap_type = call.data.get("tap_type", None)
        cleaning_mode = call.data.get("cleaning_mode", False)
        filter_status_reset = call.data.get("filter_status_reset", False)
        get_current_measurement = call.data.get("get_current_measurement", False)
        tap_amount = call.data.get("tap_amount", None)
        factory_reset = call.data.get("factory_reset", False)
        revoke_flush_confirmation = call.data.get("revoke_flush_confirmation", False)
        exec_auto_flush = call.data.get("exec_auto_flush", False)

        entry = device_registry.async_get(target)
        grohe_id = next(iter(entry.identifiers))[1]

        devices = await client.get_devices()
        device = next(
            (device for device in devices if device.appliance_id == grohe_id), None
        )

        await client.custom_command(
            device,
            co2_reset=co2_status_reset,
            filter_reset=filter_status_reset,
            flush=exec_auto_flush,
            tap_type=tap_type,
            tap_amount=tap_amount,
            clean_mode=cleaning_mode,
            get_current_measurement=get_current_measurement,
            revoke_flush_confirmation=revoke_flush_confirmation,
            factory_reset=factory_reset,
        )


    hass.services.async_register("groheblue", "tap_water", handle_tap_water)
    hass.services.async_register("groheblue", "custom_command", handle_custom_command)

    return True
