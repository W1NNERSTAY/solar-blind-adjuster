"""Binary sensor platform for Solar Blind Adjuster."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CONTROLLED_BLINDS,
    BINARY_SENSOR_SUN_FACING,
    DOMAIN,
    ICON_SUN_FACING,
)
from .coordinator import SolarBlindAdjusterCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solar Blind Adjuster binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    name = entry.data[CONF_NAME]

    binary_sensors = [
        SunFacingBinarySensor(coordinator, entry, name),
    ]

    async_add_entities(binary_sensors)


class SunFacingBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for sun facing window status."""

    def __init__(
        self,
        coordinator: SolarBlindAdjusterCoordinator,
        entry: ConfigEntry,
        name: str,
    ):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = f"{name} 직사광 여부"
        self._attr_unique_id = f"{entry.entry_id}_{BINARY_SENSOR_SUN_FACING}"
        self._attr_icon = ICON_SUN_FACING
        self._attr_device_class = BinarySensorDeviceClass.LIGHT
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": name,
            "manufacturer": "Solar Blind Adjuster",
            "model": "Solar Controller",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if sun is facing the window."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("is_sun_facing", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "sun_altitude": self.coordinator.data.get("sun_altitude"),
            "sun_azimuth": self.coordinator.data.get("sun_azimuth"),
            "window_azimuth": self.coordinator.data.get("window_azimuth"),
            ATTR_CONTROLLED_BLINDS: self.coordinator.data.get("blind_entity_ids", []),
        }
