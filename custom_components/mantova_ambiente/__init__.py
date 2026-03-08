from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import MantovaAmbienteApi
from .const import CONF_INSTANCE_NAME, CONF_ZONE_ID, CONF_ZONE_TITLE, DOMAIN
from .coordinator import MantovaAmbienteDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = MantovaAmbienteApi(hass)
    coordinator = MantovaAmbienteDataUpdateCoordinator(
        hass=hass,
        api=api,
        entry_id=entry.entry_id,
        instance_name=entry.data.get(CONF_INSTANCE_NAME, entry.title),
        zone_id=entry.data[CONF_ZONE_ID],
        zone_title=entry.data[CONF_ZONE_TITLE],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
