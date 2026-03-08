from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .api import MantovaAmbienteApi, MantovaAmbienteApiError
from .const import CONF_INSTANCE_NAME, CONF_ZONE_ID, CONF_ZONE_TITLE, DEFAULT_NAME, DOMAIN


class MantovaAmbienteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._zones: dict[str, str] = {}

    async def async_step_user(
        self, user_input: Mapping[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if not self._zones:
            api = MantovaAmbienteApi(self.hass)
            try:
                zones = await api.async_get_zones()
            except MantovaAmbienteApiError:
                return self.async_abort(reason="cannot_connect")

            self._zones = {
                str(zone["id"]): zone["title"]
                for zone in zones
                if zone.get("id") and zone.get("title")
            }

        if user_input is not None:
            zone_id = user_input[CONF_ZONE_ID]
            zone_title = self._zones[zone_id]
            instance_name = user_input[CONF_INSTANCE_NAME].strip()
            return self.async_create_entry(
                title=instance_name,
                data={
                    CONF_INSTANCE_NAME: instance_name,
                    CONF_ZONE_ID: zone_id,
                    CONF_ZONE_TITLE: zone_title,
                },
            )

        zone_options = {zone_id: title for zone_id, title in sorted(self._zones.items(), key=lambda item: item[1].lower())}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_INSTANCE_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_ZONE_ID): vol.In(zone_options),
                }
            ),
            errors=errors,
        )
