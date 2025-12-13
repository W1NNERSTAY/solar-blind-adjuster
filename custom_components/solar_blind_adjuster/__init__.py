"""The Solar Blind Adjuster integration."""
from __future__ import annotations

import logging
from datetime import datetime, time, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.core import SupportsResponse
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util
import voluptuous as vol

from .const import (
    CONF_BLIND_ENTITY_IDS,
    CONF_BLIND_ENTITY_ID,
    DOMAIN,
    SERVICE_PREVIEW_TIME,
    SERVICE_REFRESH_CALCULATION,
    SERVICE_RUN_SIMULATION,
    SERVICE_SET_STRATEGY,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Solar Blind Adjuster component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solar Blind Adjuster from a config entry."""
    from .coordinator import SolarBlindAdjusterCoordinator

    hass.data.setdefault(DOMAIN, {})

    merged_config = {**entry.data, **entry.options}

    # Create coordinator
    coordinator = SolarBlindAdjusterCoordinator(
        hass=hass,
        entry_id=entry.entry_id,
        config=merged_config,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "config": entry.data,
    }

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for config changes
    entry.async_on_unload(entry.add_update_listener(update_listener))

    async def _get_coordinator(entity_id: str) -> SolarBlindAdjusterCoordinator:
        """Resolve coordinator from an entity_id."""
        entity_registry = er.async_get(hass)
        entry = entity_registry.async_get(entity_id)
        if not entry or not entry.config_entry_id:
            raise ValueError(f"Entity {entity_id} is not associated with Solar Blind Adjuster")

        return hass.data[DOMAIN][entry.config_entry_id]["coordinator"]

    async def handle_set_strategy(call):
        coordinator = await _get_coordinator(call.data["entity_id"])
        coordinator.set_strategy(call.data["strategy"])
        await coordinator.async_request_refresh()

    async def handle_refresh(call):
        coordinator = await _get_coordinator(call.data["entity_id"])
        await coordinator.async_refresh_calculation()

    async def handle_simulation(call):
        coordinator = await _get_coordinator(call.data["entity_id"])
        date_obj = call.data["date"]
        start_raw = call.data["start_time"]
        end_raw = call.data["end_time"]

        start_time = start_raw if isinstance(start_raw, time) else dt_util.parse_time(str(start_raw))
        end_time = end_raw if isinstance(end_raw, time) else dt_util.parse_time(str(end_raw))
        interval = call.data.get("interval_minutes", 30)

        if not start_time or not end_time:
            raise ValueError("start_time and end_time must be valid HH:MM values")

        results = await coordinator.async_run_simulation(
            date_obj=date_obj,
            start_time=start_time,
            end_time=end_time,
            interval_minutes=interval,
        )

        if call.supports_response:
            return {"results": results, "controlled_blinds": coordinator.blind_entity_ids}

    async def handle_preview(call):
        coordinator = await _get_coordinator(call.data["entity_id"])
        date_obj = call.data["date"]
        time_raw = call.data["time"]

        time_obj = time_raw if isinstance(time_raw, time) else dt_util.parse_time(str(time_raw))
        if not time_obj:
            raise ValueError("time must be a valid HH:MM value")

        preview = await coordinator.async_preview_time(date_obj=date_obj, time_obj=time_obj)

        if call.supports_response:
            return {"preview": preview}

    # Register services (once per entry setup)
    if not hass.services.has_service(DOMAIN, SERVICE_SET_STRATEGY):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_STRATEGY,
            handle_set_strategy,
            schema=vol.Schema(
                {
                    vol.Required("entity_id"): str,
                    vol.Required("strategy"): str,
                }
            ),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_REFRESH_CALCULATION):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REFRESH_CALCULATION,
            handle_refresh,
            schema=vol.Schema(
                {
                    vol.Required("entity_id"): str,
                }
            ),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_RUN_SIMULATION):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RUN_SIMULATION,
            handle_simulation,
            schema=vol.Schema(
                {
                    vol.Required("entity_id"): str,
                    vol.Required("date"): vol.Date(),
                    vol.Required("start_time"): vol.Any(time, str),
                    vol.Required("end_time"): vol.Any(time, str),
                    vol.Optional("interval_minutes", default=30): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=1, max=240),
                    ),
                }
            ),
            supports_response=SupportsResponse.OPTIONAL,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_PREVIEW_TIME):
        hass.services.async_register(
            DOMAIN,
            SERVICE_PREVIEW_TIME,
            handle_preview,
            schema=vol.Schema(
                {
                    vol.Required("entity_id"): str,
                    vol.Required("date"): vol.Date(),
                    vol.Required("time"): vol.Any(time, str),
                }
            ),
            supports_response=SupportsResponse.OPTIONAL,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
