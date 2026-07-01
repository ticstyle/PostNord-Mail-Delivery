"""DataUpdateCoordinator for PostNord Mail Delivery."""

import logging
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PostNordUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching PostNord data asynchronously."""

    def __init__(self, hass: HomeAssistant, postal_code: int) -> None:
        """Initialize."""
        self.postal_code = postal_code
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from PostNord API."""
        url = f"https://portal.postnord.com/api/sendoutarrival/closest?postalCode={self.postal_code}"
        session = async_get_clientsession(self.hass)
        
        try:
            async with session.get(url, timeout=10) as resp:
                resp.raise_for_status()
                data = await resp.json()
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with PostNord API: {err}"
            ) from err

        # Säker och robust datumparsning
        delivery_text = str(data.get("delivery", "")).strip()
        arr = delivery_text.split()

        date_table = {
            "januari": "01",
            "februari": "02",
            "mars": "03",
            "april": "04",
            "maj": "05",
            "juni": "06",
            "juli": "07",
            "augusti": "08",
            "september": "09",
            "oktober": "10",
            "november": "11",
            "december": "12",
        }

        if len(arr) >= 3:
            day = arr[0].zfill(2)
            month_name = arr[1].lower().rstrip(",")
            year = arr[2]
            month = date_table.get(month_name, "01")
            formatted_date = f"{year}-{month}-{day}"

            try:
                next_date = datetime.strptime(formatted_date, "%Y-%m-%d")
                num_days = (next_date - datetime.now()).days + 1
                state_value = 0 if num_days < 0 else num_days
            except ValueError:
                state_value = delivery_text
        else:
            formatted_date = (
                delivery_text if delivery_text else "Ingen utdelning planerad"
            )
            state_value = formatted_date

        return {
            "state": state_value,
            "next_delivery": formatted_date,
            "postal_city": data.get("city", "").capitalize(),
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
