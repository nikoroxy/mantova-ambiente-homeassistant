from __future__ import annotations

from typing import Any

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_BASE_URL, RECYCLINGS_PATH, ZONE_LOOKUP_PATH


class MantovaAmbienteApi:
    def __init__(self, hass: HomeAssistant) -> None:
        self._session = async_get_clientsession(hass)

    async def async_get_zones(self) -> list[dict[str, Any]]:
        return await self._async_get_json(ZONE_LOOKUP_PATH)

    async def async_get_recyclings(self, zone_id: str) -> list[dict[str, Any]]:
        return await self._async_get_json(
            RECYCLINGS_PATH,
            params={"zone": zone_id, "from": "today"},
        )

    async def _async_get_json(
        self, path: str, params: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        url = f"{API_BASE_URL}{path}"
        try:
            async with self._session.get(url, params=params) as response:
                response.raise_for_status()
                payload = await response.json()
        except ClientError as err:
            raise MantovaAmbienteApiError(str(err)) from err

        data = payload.get("data")
        if not isinstance(data, list):
            raise MantovaAmbienteApiError("Unexpected API response")

        return data


class MantovaAmbienteApiError(Exception):
    pass
