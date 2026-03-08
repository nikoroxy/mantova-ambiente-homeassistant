from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import Any, Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MantovaAmbienteDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class MantovaAmbienteSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]
    attrs_fn: Callable[[dict[str, Any]], dict[str, Any]]


def _slugify(value: str) -> str:
    slug = value.casefold()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def _date_value(data: dict[str, Any], key: str) -> date | None:
    value = data.get(key)
    if not value:
        return None
    return date.fromisoformat(value)


def _types_value(data: dict[str, Any], key: str) -> str | None:
    day = data.get(key)
    if not day:
        return None
    values = data["schedule"].get(day, [])
    return ", ".join(values) if values else None


def _device_info(coordinator: MantovaAmbienteDataUpdateCoordinator) -> dict[str, Any]:
    data = coordinator.data
    return {
        "identifiers": {(DOMAIN, coordinator.entry_id)},
        "name": data["instance_name"],
        "manufacturer": "Mantova Ambiente",
        "model": data["zone_title"],
    }


SENSORS: tuple[MantovaAmbienteSensorEntityDescription, ...] = (
    MantovaAmbienteSensorEntityDescription(
        key="next_collection_date",
        translation_key="next_collection_date",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: _date_value(data, "next_date"),
        attrs_fn=lambda data: {
            "waste_types": data["schedule"].get(data.get("next_date") or "", []),
        },
    ),
    MantovaAmbienteSensorEntityDescription(
        key="next_collection_types",
        translation_key="next_collection_types",
        value_fn=lambda data: _types_value(data, "next_date"),
        attrs_fn=lambda data: {
            "date": data.get("next_date"),
            "upcoming": data.get("schedule", {}),
        },
    ),
    MantovaAmbienteSensorEntityDescription(
        key="today_collection_types",
        translation_key="today_collection_types",
        value_fn=lambda data: _types_value(data, "today"),
        attrs_fn=lambda data: {
            "date": data.get("today"),
        },
    ),
    MantovaAmbienteSensorEntityDescription(
        key="tomorrow_collection_types",
        translation_key="tomorrow_collection_types",
        value_fn=lambda data: _types_value(data, "tomorrow"),
        attrs_fn=lambda data: {
            "date": data.get("tomorrow"),
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MantovaAmbienteDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [
        MantovaAmbienteSensor(coordinator, entry, description) for description in SENSORS
    ]

    for waste_type in sorted(coordinator.data.get("next_dates_by_type", {})):
        entities.append(MantovaAmbienteWasteDateSensor(coordinator, entry, waste_type))

    async_add_entities(entities)


class MantovaAmbienteSensor(
    CoordinatorEntity[MantovaAmbienteDataUpdateCoordinator], SensorEntity
):
    entity_description: MantovaAmbienteSensorEntityDescription

    def __init__(
        self,
        coordinator: MantovaAmbienteDataUpdateCoordinator,
        entry: ConfigEntry,
        description: MantovaAmbienteSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self.entity_description.attrs_fn(self.coordinator.data)

    @property
    def device_info(self) -> dict[str, Any]:
        return _device_info(self.coordinator)


class MantovaAmbienteWasteDateSensor(
    CoordinatorEntity[MantovaAmbienteDataUpdateCoordinator], SensorEntity
):
    _attr_device_class = SensorDeviceClass.DATE
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MantovaAmbienteDataUpdateCoordinator,
        entry: ConfigEntry,
        waste_type: str,
    ) -> None:
        super().__init__(coordinator)
        self._waste_type = waste_type
        self._attr_name = f"Prossima raccolta {waste_type}"
        self._attr_unique_id = f"{entry.entry_id}_next_collection_{_slugify(waste_type)}"

    @property
    def native_value(self) -> date | None:
        value = self.coordinator.data.get("next_dates_by_type", {}).get(self._waste_type)
        if not value:
            return None
        return date.fromisoformat(value)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "waste_type": self._waste_type,
        }

    @property
    def device_info(self) -> dict[str, Any]:
        return _device_info(self.coordinator)
