"""Crestron HD-MD4x1-4K-E HDMI Matrix integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import HomeAssistant

from .const import DEFAULT_PORT, DOMAIN
from .select import CrestronMatrix

__all__ = ["DOMAIN"]

PLATFORMS: list[Platform] = [Platform.SELECT]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up from yaml (deprecated)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Crestron HDMI matrix from a config entry."""
    matrix = CrestronMatrix(entry.data[CONF_HOST], DEFAULT_PORT)
    await matrix.connect()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = matrix
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, matrix.close)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Crestron HDMI matrix config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        matrix: CrestronMatrix = hass.data[DOMAIN].pop(entry.entry_id)
        await matrix.close()
    return unload_ok
