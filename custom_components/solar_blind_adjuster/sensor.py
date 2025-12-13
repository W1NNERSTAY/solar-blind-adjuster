"""Sensor platform for Solar Blind Adjuster."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CONTROLLED_BLINDS,
    ATTR_CURRENT_STRATEGY,
    ATTR_DAYLIGHT_DURATION,
    ATTR_LAST_ACTION_TIME,
    ATTR_MANUAL_OVERRIDE,
    ATTR_NEXT_UPDATE,
    ATTR_SOLAR_NOON,
    ATTR_SUNRISE,
    ATTR_SUNSET,
    ATTR_WINDOW_AZIMUTH,
    DOMAIN,
    ICON_RECOMMENDED_POSITION,
    ICON_RECOMMENDED_TILT,
    ICON_SOLAR_INTENSITY,
    ICON_SUN_ALTITUDE,
    ICON_SUN_AZIMUTH,
    SENSOR_RECOMMENDED_POSITION,
    SENSOR_RECOMMENDED_TILT,
    SENSOR_SOLAR_INTENSITY,
    SENSOR_SUN_ALTITUDE,
    SENSOR_SUN_AZIMUTH,
    UNIT_DEGREES,
    UNIT_HOURS,
    UNIT_PERCENT,
)
from .coordinator import SolarBlindAdjusterCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solar Blind Adjuster sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    name = entry.data[CONF_NAME]

    sensors = [
        SunAltitudeSensor(coordinator, entry, name),
        SunAzimuthSensor(coordinator, entry, name),
        SolarIntensitySensor(coordinator, entry, name),
        RecommendedPositionSensor(coordinator, entry, name),
        RecommendedTiltSensor(coordinator, entry, name),
    ]

    async_add_entities(sensors)


class SolarBlindAdjusterSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Solar Blind Adjuster sensors."""

    def __init__(
        self,
        coordinator: SolarBlindAdjusterCoordinator,
        entry: ConfigEntry,
        name: str,
        sensor_type: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_type = sensor_type
        self._attr_name = f"{name} {sensor_type.replace('_', ' ').title()}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": name,
            "manufacturer": "Solar Blind Adjuster",
            "model": "Solar Controller",
        }

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return common state attributes."""
        if not self.coordinator.data:
            return {}

        blinds = self.coordinator.data.get("blind_entity_ids", [])

        attrs = {
            ATTR_SUNRISE: self._format_datetime(self.coordinator.data.get("sunrise")),
            ATTR_SUNSET: self._format_datetime(self.coordinator.data.get("sunset")),
            ATTR_SOLAR_NOON: self._format_datetime(self.coordinator.data.get("solar_noon")),
            ATTR_DAYLIGHT_DURATION: f"{self.coordinator.data.get('daylight_duration', 0):.2f} {UNIT_HOURS}",
            ATTR_CURRENT_STRATEGY: self.coordinator.data.get("active_strategy"),
            ATTR_MANUAL_OVERRIDE: self.coordinator.data.get("manual_override", False),
            ATTR_WINDOW_AZIMUTH: f"{self.coordinator.data.get('window_azimuth', 0)}{UNIT_DEGREES}",
            ATTR_NEXT_UPDATE: self._format_datetime(self.coordinator.data.get("next_update")),
            ATTR_CONTROLLED_BLINDS: blinds,
        }

        # Add last action time if available
        last_action = self.coordinator.data.get("last_action_time")
        if last_action:
            attrs[ATTR_LAST_ACTION_TIME] = self._format_datetime(last_action)

        return attrs

    def _format_datetime(self, dt: datetime | None) -> str | None:
        """Format datetime for display."""
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class SunAltitudeSensor(SolarBlindAdjusterSensorBase):
    """Sensor for sun altitude angle."""

    def __init__(
        self,
        coordinator: SolarBlindAdjusterCoordinator,
        entry: ConfigEntry,
        name: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, entry, name, SENSOR_SUN_ALTITUDE)
        self._attr_icon = ICON_SUN_ALTITUDE
        self._attr_native_unit_of_measurement = UNIT_DEGREES
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("sun_altitude")


class SunAzimuthSensor(SolarBlindAdjusterSensorBase):
    """Sensor for sun azimuth angle."""

    def __init__(
        self,
        coordinator: SolarBlindAdjusterCoordinator,
        entry: ConfigEntry,
        name: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, entry, name, SENSOR_SUN_AZIMUTH)
        self._attr_icon = ICON_SUN_AZIMUTH
        self._attr_native_unit_of_measurement = UNIT_DEGREES
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("sun_azimuth")


class SolarIntensitySensor(SolarBlindAdjusterSensorBase):
    """Sensor for relative solar intensity."""

    def __init__(
        self,
        coordinator: SolarBlindAdjusterCoordinator,
        entry: ConfigEntry,
        name: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, entry, name, SENSOR_SOLAR_INTENSITY)
        self._attr_icon = ICON_SOLAR_INTENSITY
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("solar_intensity")


class RecommendedPositionSensor(SolarBlindAdjusterSensorBase):
    """Sensor for recommended blind position."""

    def __init__(
        self,
        coordinator: SolarBlindAdjusterCoordinator,
        entry: ConfigEntry,
        name: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, entry, name, SENSOR_RECOMMENDED_POSITION)
        self._attr_icon = ICON_RECOMMENDED_POSITION
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("recommended_position")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        attrs = super().extra_state_attributes
        if self.coordinator.data:
            attrs["should_update"] = self.coordinator.data.get("should_update", False)
        return attrs


class RecommendedTiltSensor(SolarBlindAdjusterSensorBase):
    """Sensor for recommended blind tilt angle."""

    def __init__(
        self,
        coordinator: SolarBlindAdjusterCoordinator,
        entry: ConfigEntry,
        name: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, entry, name, SENSOR_RECOMMENDED_TILT)
        self._attr_icon = ICON_RECOMMENDED_TILT
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("recommended_tilt")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        attrs = super().extra_state_attributes
        if self.coordinator.data:
            attrs["should_update"] = self.coordinator.data.get("should_update", False)
        return attrs
