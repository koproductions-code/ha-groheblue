import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .options_flow import GroheBlueOptionsFlowHandler

DOMAIN = "groheblue"


class MyIntegrationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for My Integration."""

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input["email"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("email"): str,
                vol.Required("password"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry,
    ) -> GroheBlueOptionsFlowHandler:
        """Create the options flow."""
        return GroheBlueOptionsFlowHandler(config_entry)
