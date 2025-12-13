"""Switch platform for Solar Blind Adjuster."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_CONTROLLED_BLINDS, DOMAIN
from .coordinator import SolarBlindAdjusterCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solar Blind Adjuster switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    name = entry.data[CONF_NAME]

    switches = [
        ManualModeSwitch(coordinator, entry, name),
    ]

    async_add_entities(switches)


class ManualModeSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to toggle manual override mode."""

    def __init__(
        self,
        coordinator: SolarBlindAdjusterCoordinator,
        entry: ConfigEntry,
        name: str,
    ):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = f"{name} Manual Mode"
        self._attr_unique_id = f"{entry.entry_id}_manual_mode"
        self._attr_icon = "mdi:hand-back-right"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": name,
            "manufacturer": "Solar Blind Adjuster",
            "model": "Solar Controller",
        }

    @property
    def is_on(self) -> bool:
        """Return true if manual mode is enabled."""
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("manual_override", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on manual mode."""
        self.coordinator.set_manual_override(True)
        await self.coordinator.async_request_refresh()
        _LOGGER.info("Manual mode enabled")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off manual mode."""
        self.coordinator.set_manual_override(False)
        await self.coordinator.async_request_refresh()
        _LOGGER.info("Manual mode disabled")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "active_strategy": self.coordinator.data.get("active_strategy"),
            "last_update": self.coordinator.data.get("calculation_time"),
            ATTR_CONTROLLED_BLINDS: self.coordinator.data.get("blind_entity_ids", []),
        }
