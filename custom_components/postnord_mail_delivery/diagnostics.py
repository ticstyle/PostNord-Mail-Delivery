"""Diagnostics platform for PostNord Mail Delivery."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_POSTALCODE, DOMAIN
from .coordinator import PostNordUpdateCoordinator

TO_REDACT = {CONF_POSTALCODE}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: PostNordUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Gather and redact the configuration entry data
    config_entry_data = async_redact_data(entry.as_dict(), TO_REDACT)

    # Gather and redact the current state from the coordinator
    coordinator_data: dict[str, Any] = {}
    if coordinator.data is not None:
        coordinator_data = dict(coordinator.data)

    # Redact the postal code if it leaked into the coordinator data dict
    redacted_coordinator_data = async_redact_data(coordinator_data, TO_REDACT)

    return {
        "config_entry": config_entry_data,
        "coordinator_data": redacted_coordinator_data,
    }
  
