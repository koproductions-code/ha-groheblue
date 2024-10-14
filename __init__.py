from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr
from datetime import timedelta
import logging

from .GroheClient.tap_controller import check_tap_params, execute_tap_command, get_dashboard_data
from .GroheClient.base import GroheClient
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

DOMAIN = "groheblue"
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the Grohe Blue component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Grohe Blue component."""

    email = entry.data.get("email")
    password = entry.data.get("password")

    client = GroheClient(email=email, password=password)
    await client._initialize_tokens()

    coordinator = GroheDataUpdateCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "1e7f471f-3b1e-40e5-a665-c1aaa898eae9")},
        name="My GROHE Blue Home",
        manufacturer="Grohe",
        model="Blue Home",
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    async def handle_tap_water(call):
        tap_type = call.data.get('type')
        amount = call.data.get('amount')

        await execute_tap_command(tap_type, amount)

    hass.services.async_register(DOMAIN, 'tap_water', handle_tap_water)
    return True

class GroheDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Grohe data from a single endpoint."""

    def __init__(self, hass: HomeAssistant, client: GroheClient):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Grohe Blue Data Coordinator",
            update_interval=timedelta(minutes=5),
        )
        self.client = client

    async def _async_update_data(self):
        """Fetch data from GroheClient."""
        data = await get_dashboard_data(self.client.get_access_token())
        remaining_co2 = data['locations'][0]['rooms'][0]['appliances'][0]['data_latest']['measurement']['remaining_co2']
        return {"remaining_co2": remaining_co2}
