"""Sensor platform for PostNord Mail Delivery."""

import json
import logging
import os

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
)
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_POSTALCODE, DEVICE_AUTHOR, DEVICE_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


def _get_local_strings(dir_path: str, lang: str) -> dict:
    """Load friendly status strings from local translation files.

    This runs inside an executor thread to prevent blocking the main event loop.
    """
    file_path = os.path.join(dir_path, "translations", f"{lang}.json")

    if not os.path.exists(file_path) and "-" in lang:
        file_path = os.path.join(
            dir_path, "translations", f"{lang.split('-')[0]}.json"
        )

    if not os.path.exists(file_path):
        file_path = os.path.join(dir_path, "strings.json")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f).get("friendly_status", {})
    except Exception as err:
        _LOGGER.error("Failed to load local status translations: %s", err)
        return {}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    postal_code = config_entry.data[CONF_POSTALCODE]

    lang = hass.config.language if hass else "en"
    dir_path = os.path.dirname(os.path.realpath(__file__))

    status_strings = await hass.async_add_executor_job(
        _get_local_strings, dir_path, lang
    )

    async_add_entities(
        [PostNordDeliverySensor(coordinator, postal_code, status_strings)]
    )


class PostNordDeliverySensor(CoordinatorEntity, SensorEntity):
    """Representation of a PostNord Delivery Sensor."""

    def __init__(self, coordinator, postal_code, status_strings):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._postal_code = postal_code
        self._status_strings = status_strings

        p_code = str(postal_code).replace(" ", "")
        if len(p_code) == 5:
            self._formatted_postal_code = f"{p_code[:3]} {p_code[3:]}"
        else:
            self._formatted_postal_code = p_code

        self.entity_id = f"sensor.{DOMAIN}_{self._postal_code}"
        self._attr_unique_id = f"{DOMAIN}_{self._postal_code}_sensor"

        self._attr_has_entity_name = True
        self._attr_name = f"Delivery for {self._postal_code}"
        self._attr_icon = "mdi:mailbox-up-outline"
        
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, DEVICE_NAME)},
            ATTR_NAME: "PostNord",  
            ATTR_MANUFACTURER: DEVICE_AUTHOR,
            ATTR_MODEL: "PostNord Mail Delivery",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def native_value(self):
        """Return the state of the sensor (days left or text)."""
        return self.coordinator.data.get("state")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        state = self.coordinator.data.get("state")

        today = self._status_strings.get("today", "Today")
        tomorrow = self._status_strings.get("tomorrow", "Tomorrow")
        in_days_fmt = self._status_strings.get("in_days", "In {days} days")
        no_delivery = self._status_strings.get(
            "no_delivery", "No delivery scheduled"
        )

        if isinstance(state, int):
            if state == 0:
                friendly_status = today
            elif state == 1:
                friendly_status = tomorrow
            else:
                try:
                    friendly_status = in_days_fmt.format(days=state)
                except KeyError:
                    friendly_status = f"In {state} days"
        else:
            if state == "Ingen utdelning planerad":
                friendly_status = no_delivery
            else:
                friendly_status = state

        last_update = self.coordinator.data.get("last_update")
        if hasattr(last_update, "strftime"):
            last_update_formatted = last_update.strftime("%Y-%m-%d %H:%M:%S")
        else:
            last_update_formatted = str(last_update)

        next_delivery = self.coordinator.data.get("next_delivery")
        if hasattr(next_delivery, "strftime"):
            next_delivery_formatted = next_delivery.strftime("%Y-%m-%d")
        else:
            next_delivery_formatted = str(next_delivery)

        return {
            "last_update": last_update_formatted,
            "postal_city": self.coordinator.data.get("postal_city"),
            "next_delivery": next_delivery_formatted,
            "postal_code": self._formatted_postal_code,
            "friendly_status": friendly_status,
        }
