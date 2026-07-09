"""Sensor platform for PostNord Mail Delivery."""

from datetime import date, datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_POSTALCODE, DEVICE_AUTHOR, DOMAIN
from .coordinator import PostNordUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

STATUS_STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "today": "Today",
        "tomorrow": "Tomorrow",
        "in_days": "In {days} days",
        "no_delivery": "No delivery scheduled",
    },
    "sv": {
        "today": "I dag",
        "tomorrow": "I morgon",
        "in_days": "Om {days} dagar",
        "no_delivery": "Ingen utdelning planerad",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform with multiple entities."""
    coordinator: PostNordUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    postal_code: str = config_entry.data[CONF_POSTALCODE]

    sensor_types = ["days", "friendly_en", "friendly_sv", "date", "city"]

    async_add_entities(
        [
            PostNordDeliverySensor(coordinator, postal_code, s_type)
            for s_type in sensor_types
        ]
    )


class PostNordDeliverySensor(
    CoordinatorEntity[PostNordUpdateCoordinator], SensorEntity
):
    """Representation of a versatile PostNord Delivery Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PostNordUpdateCoordinator,
        postal_code: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._postal_code = str(postal_code)
        self._sensor_type = sensor_type

        # Format the postal code cleanly (e.g. 617 92)
        p_code = self._postal_code.replace(" ", "")
        self._formatted_postal_code = (
            f"{p_code[:3]} {p_code[3:]}" if len(p_code) == 5 else p_code
        )

        # Set entity properties based on sensor type
        if self._sensor_type == "days":
            self.entity_id = f"sensor.{DOMAIN}_{self._postal_code}"
            self._attr_unique_id = f"{DOMAIN}_{self._postal_code}_sensor"
            self._attr_name = "Days until delivery"
            self._attr_icon = "mdi:mailbox-up-outline"
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = UnitOfTime.DAYS
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
            self._attr_device_class = SensorDeviceClass.DATE
        elif self._sensor_type == "city":
            self.entity_id = f"sensor.{DOMAIN}_{self._postal_code}_postal_city"
            self._attr_unique_id = f"{DOMAIN}_{self._postal_code}_postal_city"
            self._attr_name = "Postal City"
            self._attr_icon = "mdi:map-marker-outline"

        # Attach device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._postal_code)},
            name=f"PostNord {self._formatted_postal_code}",
            manufacturer=DEVICE_AUTHOR,
            model="PostNord Mail Delivery",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.postnord.se/vara-verktyg/sok-utdelningsdag",
        )

    def _compute_status_by_lang(self, lang_key: str, state: Any) -> str:
        """Compute friendly status text for a specific language."""
        strings = STATUS_STRINGS.get(lang_key, STATUS_STRINGS["en"])
        today = strings["today"]
        tomorrow = strings["tomorrow"]
        in_days_fmt = strings["in_days"]
        no_delivery = strings["no_delivery"]

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
    def native_value(self) -> Any:
        """Return the computational state computed dynamically for this sensor type."""
        if self.coordinator.data is None:
            return None

        state = self.coordinator.data.get("state")

        if self._sensor_type == "days":
            return state

        if self._sensor_type == "friendly_en":
            return self._compute_status_by_lang("en", state)

        if self._sensor_type == "friendly_sv":
            return self._compute_status_by_lang("sv", state)

        if self._sensor_type == "date":
            next_delivery = self.coordinator.data.get("next_delivery")
            if isinstance(next_delivery, datetime):
                return next_delivery.date()
            if isinstance(next_delivery, date):
                return next_delivery
            if isinstance(next_delivery, str):
                try:
                    return datetime.strptime(next_delivery.strip(), "%Y-%m-%d").date()
                except ValueError:
                    return None
            return None

        if self._sensor_type == "city":
            return self.coordinator.data.get("postal_city")

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return basic metadata attributes."""
        if self.coordinator.data is None:
            return {
                "last_update": None,
                "postal_code": self._formatted_postal_code,
            }

        last_update = self.coordinator.data.get("last_update")

        if isinstance(last_update, (datetime, date)):
            last_update_formatted: str | None = last_update.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        elif last_update is not None:
            last_update_formatted = str(last_update)
        else:
            last_update_formatted = None

        return {
            "last_update": last_update_formatted,
            "postal_code": self._formatted_postal_code,
        }
