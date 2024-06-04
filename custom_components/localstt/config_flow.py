from __future__ import annotations

from typing import Any
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "LocalSTT"
NAME = "Local-Speech-To-Text"
WS_URL = "WS_URL"

class ConfigFlowHandler(ConfigFlow, domain=DOMAIN):

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        
        data_schema = vol.Schema({})
        if self._async_current_entries():
            return self.async_abort(reason="single_instance")

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(WS_URL, default="ws://localhost:6006"): cv.string,
                    },
                ),
                errors={},
            )
        return self.async_create_entry(title = NAME, data=user_input)