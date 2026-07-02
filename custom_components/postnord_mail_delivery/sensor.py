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


def _load_status_strings(dir_path: str, lang: str) -> dict:
    """Load friendly status strings from a specific language file."""
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
        _LOGGER.error("Failed to load local status translations for %s: %s", lang, err)
        return {}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform with multiple entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    postal_code = config_entry.data[CONF_POSTALCODE]

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Läs in både engelska och svenska strängar i bakgrundstrådar
    strings_en = await hass.async_add_executor_job(_load_status_strings, dir_path, "en")
    strings_sv = await hass.async_add_executor_job(_load_status_strings, dir_path, "sv")

    translation_package = {
        "en": strings_en,
        "sv": strings_sv,
    }

    # Vi skapar nu 5 unika sensorer, inklusive en för EN och en för SV
    sensor_types = ["days", "friendly_en", "friendly_sv", "date", "city"]
    
    async_add_entities([
        PostNordDeliverySensor(coordinator, postal_code, s_type, translation_package)
        for s_type in sensor_types
    ])


class PostNordDeliverySensor(CoordinatorEntity, SensorEntity):
    """Representation of a versatile PostNord Delivery Sensor."""

    def __init__(self, coordinator, postal_code, sensor_type, translation_package):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._postal_code = postal_code
        self._sensor_type = sensor_type
        self._translation_package = translation_package

        # Formatera postnumret snyggt (t.ex. 617 92)
        p_code = str(postal_code).replace(" ", "")
        self._formatted_postal_code = f"{p_code[:3]} {p_code[3:]}" if len(p_code) == 5 else p_code

        # Dynamisk namngivning och unika IDn baserat på sensortyp
        if self._sensor_type == "days":
            self.entity_id = f"sensor.{DOMAIN}_{self._postal_code}"
            self._attr_unique_id = f"{DOMAIN}_{self._postal_code}_sensor"
            self._attr_name = "Days until delivery"
            self._attr_icon = "mdi:mailbox-up-outline"
        elif self._sensor_type == "friendly_en":
            self.entity_id = f"sensor.{DOMAIN}_{self._postal_code}_friendly_status_en"
            self._attr_unique_id = f"{DOMAIN}_{self._postal_code}_friendly_status_en"
            self._attr_name = "Friendly Status (EN)"
            self._attr_icon = "mdi:chat-processing-outline"
        elif self._sensor_type == "friendly_sv":
            self.entity_id = f"sensor.{DOMAIN}_{self._postal_code}_friendly_status_sv"
            self._attr_unique_id = f"{DOMAIN}_{self._postal_code}_friendly_status_sv"
            self._attr_name = "Friendly Status (SV)"
            self._attr_icon = "mdi:chat-processing-outline"
        elif self._sensor_type == "date":
            self.entity_id = f"sensor.{DOMAIN}_{self._postal_code}_next_delivery"
            self._attr_unique_id = f"{DOMAIN}_{self._postal_code}_next_delivery"
            self._attr_name = "Next Delivery"
            self._attr_icon = "mdi:calendar-clock"
        elif self._sensor_type == "city":
            self.entity_id = f"sensor.{DOMAIN}_{self._postal_code}_postal_city"
            self._attr_unique_id = f"{DOMAIN}_{self._postal_code}_postal_city"
            self._attr_name = "Postal City"
            self._attr_icon = "mdi:map-marker-outline"

        # Gruppera alla 5 sensorer snyggt under samma PostNord-enhet
        self._attr_has_entity_name = True
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, self._postal_code)},
            ATTR_NAME: f"PostNord {self._formatted_postal_code}",
            ATTR_MANUFACTURER: DEVICE_AUTHOR,
            ATTR_MODEL: "PostNord Mail Delivery",
            "entry_type": DeviceEntryType.SERVICE,
        }

    def _compute_status_by_lang(self, lang_key: str, state) -> str:
        """Helper to compute friendly status text for a specific language dictionary."""
        strings = self._translation_package.get(lang_key, {})
        today = strings.get("today", "Today" if lang_key == "en" else "I dag")
        tomorrow = strings.get("tomorrow", "Tomorrow" if lang_key == "en" else "I morgon")
        in_days_fmt = strings.get("in_days", "In {days} days" if lang_key == "en" else "Om {days} dagar")
        no_delivery = strings.get("no_delivery", "No delivery scheduled" if lang_key == "en" else "Ingen utdelning planerad")

        if isinstance(state, int):
            if state == 0:
                return today
            if state == 1:
                return tomorrow
            try:
                return in_days_fmt.format(days=state)
            except KeyError:
                return f"In {state} days" if lang_key == "en" else f"Om {state} dagar"
        
        return no_delivery if state == "Ingen utdelning planerad" else str(state)

    @property
    def native_value(self):
        """Return the computational state computed dynamically for this sensor type."""
        state = self.coordinator.data.get("state")

        if self._sensor_type == "days":
            return state

        if self._sensor_type == "friendly_en":
            return self._compute_status_by_lang("en", state)

        if self._sensor_type == "friendly_sv":
            return self._compute_status_by_lang("sv", state)

        if self._sensor_type == "date":
            next_delivery = self.coordinator.data.get("next_delivery")
            if hasattr(next_delivery, "strftime"):
                return next_delivery.strftime("%Y-%m-%d")
            return str(next_delivery)

        if self._sensor_type == "city":
            return self.coordinator.data.get("postal_city")

        return None

    @property
    def extra_state_attributes(self):
        """Return basic metadata attributes."""
        last_update = self.coordinator.data.get("last_update")
        
        if hasattr(last_update, "strftime"):
            last_update_formatted = last_update.strftime("%Y-%m-%d %H:%M:%S")
        else:
            last_update_formatted = str(last_update)

        return {
            "last_update": last_update_formatted,
            "postal_code": self._formatted_postal_code,
        }
