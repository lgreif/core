"""Select entity for the Crestron HDMI matrix."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DEFAULT_PORT, DOMAIN


class CrestronMatrix:
    """Handle communication with the Crestron matrix."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize connection details."""
        self.host = host
        self.port = port
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self._callbacks: list[Callable[[int], None]] = []
        self._current_route = 1

    async def connect(self) -> None:
        """Open the connection and start reader task."""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        self._reader_task = asyncio.create_task(self._read_loop())
        await self.query_route()

    async def close(self) -> None:
        """Close the connection."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        if hasattr(self, "_reader_task"):
            self._reader_task.cancel()

    async def _read_loop(self) -> None:
        """Read lines and dispatch callbacks."""
        assert self.reader
        while line := await self.reader.readline():
            text = line.decode().strip()
            if text.startswith("event output 1 route "):
                self._current_route = int(text.split()[-1])
                for cb in self._callbacks:
                    cb(self._current_route)

    async def send(self, command: str) -> None:
        """Send a command to the matrix."""
        assert self.writer
        self.writer.write((command + "\n").encode())
        await self.writer.drain()

    async def query_route(self) -> None:
        """Query current route."""
        await self.send("show output 1 route")

    async def set_route(self, output: int, input_no: int) -> None:
        """Route an input to the output."""
        await self.send(f"conf output {output} route {input_no}")

    def register_callback(self, callback: Callable[[int], None]) -> None:
        """Register a callback for route updates."""
        self._callbacks.append(callback)

    @property
    def route(self) -> int:
        """Return current routed input."""
        return self._current_route


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the select platform."""
    host = config[CONF_HOST]
    port = DEFAULT_PORT

    matrix = CrestronMatrix(host, port)
    await matrix.connect()
    hass.data.setdefault(DOMAIN, {})[host] = matrix

    async def _close(_: Event) -> None:
        await matrix.close()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _close)

    async_add_entities([MatrixOutputSelect(matrix)], True)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select entity from config entry."""
    matrix: CrestronMatrix = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MatrixOutputSelect(matrix)], True)


class MatrixOutputSelect(SelectEntity):
    """Representation of the matrix output."""

    _attr_options = ["1", "2", "3", "4"]
    _attr_has_entity_name = True
    _attr_translation_key = "input"

    def __init__(self, matrix: CrestronMatrix) -> None:
        """Initialize the select entity."""
        self.matrix = matrix
        self._attr_name = "HDMI Output 1 Source"
        self._attr_unique_id = f"{matrix.host}-output1"
        self._attr_current_option = None

    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added."""

        @callback
        def update_from_event(route: int) -> None:
            self._attr_current_option = str(route)
            self.async_write_ha_state()

        self.matrix.register_callback(update_from_event)

    async def async_update(self) -> None:
        """Update the current selected option."""
        await self.matrix.query_route()
        self._attr_current_option = str(self.matrix.route)

    async def async_select_option(self, option: str) -> None:
        """Handle selecting an option from Home Assistant."""
        await self.matrix.set_route(1, int(option))
        self._attr_current_option = option
