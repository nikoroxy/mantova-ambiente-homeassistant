from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MantovaAmbienteApi, MantovaAmbienteApiError
from .const import UPDATE_INTERVAL

LOGGER = logging.getLogger(__name__)


class MantovaAmbienteDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(
        self,
        hass: HomeAssistant,
        api: MantovaAmbienteApi,
        entry_id: str,
        instance_name: str,
        zone_id: str,
        zone_title: str,
    ) -> None:
        super().__init__(
            hass,
            logger=LOGGER,
            name="Mantova Ambiente",
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api
        self.entry_id = entry_id
        self.instance_name = instance_name
        self.zone_id = zone_id
        self.zone_title = zone_title

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            recyclings = await self.api.async_get_recyclings(self.zone_id)
        except MantovaAmbienteApiError as err:
            raise UpdateFailed(err) from err

        schedule: dict[str, list[str]] = defaultdict(list)
        next_dates_by_type: dict[str, str] = {}
        raw_items: list[dict[str, Any]] = []

        for item in recyclings:
            title = item.get("title")
            params = item.get("params") or {}
            modalita = params.get("modalita")
            collections = item.get("collections") or []

            raw_items.append(
                {
                    "id": item.get("id"),
                    "title": title,
                    "modalita": modalita,
                    "collections": collections,
                }
            )

            if not title or modalita != "porta a porta":
                continue

            parsed_dates: list[str] = []

            for collection in collections:
                try:
                    day = datetime.strptime(collection, "%Y-%m-%d %H:%M:%S").date()
                except ValueError:
                    continue
                key = day.isoformat()
                parsed_dates.append(key)
                if title not in schedule[key]:
                    schedule[key].append(title)

            if parsed_dates:
                next_dates_by_type[title] = min(parsed_dates)

        for titles in schedule.values():
            titles.sort()

        ordered_dates = sorted(schedule)
        next_date = ordered_dates[0] if ordered_dates else None
        today_dt = datetime.now().date()
        today = today_dt.isoformat()
        tomorrow = (today_dt + timedelta(days=1)).isoformat()

        return {
            "zone_id": self.zone_id,
            "zone_title": self.zone_title,
            "instance_name": self.instance_name,
            "schedule": dict(schedule),
            "next_dates_by_type": next_dates_by_type,
            "next_date": next_date,
            "today": today,
            "tomorrow": tomorrow,
            "raw_items": raw_items,
        }
