from homeassistant import config_entries
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

DOMAIN = "groheblue"


class GroheBlueOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Required(
                "polling_interval",
                default=self.config_entry.options.get("polling_interval", 300),
                msg="Set a custom polling interval in seconds. Default is 300 seconds.",
            ): cv.positive_int
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))
