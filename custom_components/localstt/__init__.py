"""The STT component."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

platforms = [Platform.STT]

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(config_entry, platforms)
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry)-> bool:
    return await hass.config_entries.async_unload_platforms(config_entry, platforms)

