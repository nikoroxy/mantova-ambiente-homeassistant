from __future__ import annotations

from dataclasses import dataclass
import re

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MantovaAmbienteDataUpdateCoordinator


def _slugify(value: str) -> str:
    slug = value.casefold()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def _device_info(coordinator: MantovaAmbienteDataUpdateCoordinator) -> dict[str, object]:
    data = coordinator.data
    return {
        "identifiers": {(DOMAIN, coordinator.entry_id)},
        "name": data["instance_name"],
        "manufacturer": "Mantova Ambiente",
        "model": data["zone_title"],
    }


@dataclass(frozen=True, kw_only=True)
class MantovaAmbienteBinarySensorEntityDescription(BinarySensorEntityDescription):
    day_key: str
    name_prefix: str


DESCRIPTIONS: tuple[MantovaAmbienteBinarySensorEntityDescription, ...] = (
    MantovaAmbienteBinarySensorEntityDescription(
        key="today",
        day_key="today",
        name_prefix="Raccolta oggi",
    ),
    MantovaAmbienteBinarySensorEntityDescription(
        key="tomorrow",
        day_key="tomorrow",
        name_prefix="Raccolta domani",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MantovaAmbienteDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = []

    for waste_type in sorted(coordinator.data.get("next_dates_by_type", {})):
        for description in DESCRIPTIONS:
            entities.append(
                MantovaAmbienteCollectionBinarySensor(
                    coordinator,
                    entry,
                    waste_type,
                    description,
                )
            )

    async_add_entities(entities)


class MantovaAmbienteCollectionBinarySensor(
    CoordinatorEntity[MantovaAmbienteDataUpdateCoordinator], BinarySensorEntity
):
    entity_description: MantovaAmbienteBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MantovaAmbienteDataUpdateCoordinator,
        entry: ConfigEntry,
        waste_type: str,
        description: MantovaAmbienteBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self._waste_type = waste_type
        self.entity_description = description
        self._attr_name = f"{description.name_prefix} {waste_type}"
        self._attr_unique_id = (
            f"{entry.entry_id}_{description.key}_collection_{_slugify(waste_type)}"
        )

    @property
    def is_on(self) -> bool:
        day = self.coordinator.data.get(self.entity_description.day_key)
        if not day:
            return False
        return self._waste_type in self.coordinator.data.get("schedule", {}).get(day, [])

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        return {
            "waste_type": self._waste_type,
            "date": self.coordinator.data.get(self.entity_description.day_key),
        }

    @property
    def device_info(self) -> dict[str, object]:
        return _device_info(self.coordinator)
