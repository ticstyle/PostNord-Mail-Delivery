"""Config flow for PostNord Mail Delivery."""

import logging
import aiohttp
import voluptuous as vol

from homeassistant import config_entries

from .const import CONF_POSTALCODE, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PostNordMailDeliveryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PostNord Mail Delivery."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        data_schema = vol.Schema(
            {
                vol.Required(CONF_POSTALCODE, default=10000): vol.All(
                    vol.Coerce(int), vol.Range(min=10000, max=99999)
                )
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=data_schema)

        postalcode = user_input[CONF_POSTALCODE]
        url = f"https://portal.postnord.com/api/sendoutarrival/closest?postalCode={postalcode}"

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    postal_city = data["city"].capitalize()
        except Exception:
            return self.async_show_form(
                step_id="user",
                data_schema=data_schema,
                errors={"base": "invalid_postal_code"},
            )

        await self.async_set_unique_id(f"{DOMAIN}_{postalcode}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"{postal_city} {postalcode}",
            data={CONF_POSTALCODE: postalcode},
        )
