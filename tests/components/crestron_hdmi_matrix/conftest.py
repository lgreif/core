"""Fixtures for the Crestron HDMI matrix tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Mock async_setup_entry to prevent side effects."""
    with patch(
        "homeassistant.components.crestron_hdmi_matrix.async_setup_entry",
        return_value=True,
    ) as mock_setup:
        yield mock_setup
