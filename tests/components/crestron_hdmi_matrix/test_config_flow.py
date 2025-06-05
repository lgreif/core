"""Test the Crestron HDMI matrix config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant.components.crestron_hdmi_matrix.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_user_flow(hass: HomeAssistant, mock_setup_entry: AsyncMock) -> None:
    """Test a successful user initiated flow."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] is FlowResultType.FORM

    with patch("asyncio.open_connection"), patch(
        "homeassistant.components.crestron_hdmi_matrix.config_flow._validate_host",
        return_value=True,
    ):
        result2 = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_HOST: "1.2.3.4"})
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["data"] == {CONF_HOST: "1.2.3.4"}
    assert len(mock_setup_entry.mock_calls) == 1


async def test_cannot_connect(hass: HomeAssistant, mock_setup_entry: AsyncMock) -> None:
    """Test handling connection failures."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    with patch("homeassistant.components.crestron_hdmi_matrix.config_flow._validate_host", return_value=False):
        result2 = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_HOST: "1.2.3.4"})

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}
