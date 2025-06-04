"""Config flow for Crestron HD-MD4x1-4K-E HDMI Matrix."""

from __future__ import annotations

import asyncio
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import DEFAULT_PORT, DOMAIN


async def _validate_host(hass: HomeAssistant, host: str) -> bool:
    """Test if we can connect to the matrix."""
    try:
        await asyncio.wait_for(asyncio.open_connection(host, DEFAULT_PORT), 5)
    except OSError:
        return False
    return True


class CrestronConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a Crestron HD-MD4x1-4K-E config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            if await _validate_host(self.hass, host):
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=host, data=user_input)
            errors["base"] = "cannot_connect"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )
