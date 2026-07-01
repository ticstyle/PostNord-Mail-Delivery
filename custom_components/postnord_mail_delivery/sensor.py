"""Sensor platform for PostNord Mail Delivery."""

import logging

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


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    postal_code = config_entry.data[CONF_POSTALCODE]
    async_add_entities([PostNordDeliverySensor(coordinator, postal_code)])


class PostNordDeliverySensor(CoordinatorEntity, SensorEntity):
    """Representation of a PostNord Delivery Sensor."""

    def __init__(self, coordinator, postal_code):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._postal_code = postal_code

        # Tvingar fram det exakta namnet (t.ex. sensor.postnord_mail_delivery_61792)
        self.entity_id = f"sensor.{DOMAIN}_{self._postal_code}"

        self._attr_unique_id = f"{DOMAIN}_{self._postal_code}_sensor"
        self._attr_name = f"PostNord Delivery {self._postal_code}"
        self._attr_icon = "mdi:mailbox-up-outline"
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, DEVICE_NAME)},
            ATTR_NAME: DEVICE_NAME,
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
        return {
            "last_update": self.coordinator.data.get("last_update"),
            "postal_city": self.coordinator.data.get("postal_city"),
            "next_delivery": self.coordinator.data.get("next_delivery"),
            "postal_code": self._postal_code,
        }
        
