"""Data update coordinator for Solar Blind Adjuster."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .blind_controller import BlindController, BlindState, WindowConfig
from .const import (
    CONF_BLIND_ENTITY_ID,
    CONF_CHANGE_THRESHOLD,
    CONF_ELEVATION,
    CONF_HYBRID_SCHEDULE,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MIN_ACTION_INTERVAL,
    CONF_POSITION_LIMITS,
    CONF_STRATEGY,
    CONF_SUN_ALTITUDE_THRESHOLD,
    CONF_SUN_FACING_TOLERANCE,
    CONF_SUNRISE_ACTION,
    CONF_SUNSET_ACTION,
    CONF_TILT_LIMITS,
    CONF_UPDATE_INTERVAL,
    CONF_WINDOW_AZIMUTH,
    DEFAULT_CHANGE_THRESHOLD,
    DEFAULT_MIN_ACTION_INTERVAL,
    DEFAULT_POSITION_MAX,
    DEFAULT_POSITION_MIN,
    DEFAULT_STRATEGY,
    DEFAULT_SUN_ALTITUDE_THRESHOLD,
    DEFAULT_SUN_FACING_TOLERANCE,
    DEFAULT_TILT_MAX,
    DEFAULT_TILT_MIN,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .solar_calculator import SolarCalculator
from .strategy_engine import StrategyEngine

_LOGGER = logging.getLogger(__name__)


class SolarBlindAdjusterCoordinator(DataUpdateCoordinator):
    """Coordinator to manage solar blind adjuster data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        config: dict[str, Any],
    ):
        """Initialize the coordinator.

        Args:
            hass: HomeAssistant instance
            entry_id: Config entry ID
            config: Configuration dictionary
        """
        self.entry_id = entry_id
        self.config = config

        # Extract configuration
        self.blind_entity_id = config[CONF_BLIND_ENTITY_ID]
        latitude = config.get(CONF_LATITUDE, hass.config.latitude)
        longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
        elevation = config.get(CONF_ELEVATION, hass.config.elevation or 0)
        timezone = str(hass.config.time_zone)

        # Window configuration
        window_azimuth = config[CONF_WINDOW_AZIMUTH]
        position_limits = config.get(CONF_POSITION_LIMITS, {})
        tilt_limits = config.get(CONF_TILT_LIMITS, {})

        window_config = WindowConfig(
            azimuth=window_azimuth,
            position_min=position_limits.get("min", DEFAULT_POSITION_MIN),
            position_max=position_limits.get("max", DEFAULT_POSITION_MAX),
            tilt_min=tilt_limits.get("min", DEFAULT_TILT_MIN),
            tilt_max=tilt_limits.get("max", DEFAULT_TILT_MAX),
        )

        # Control parameters
        change_threshold = config.get(CONF_CHANGE_THRESHOLD, DEFAULT_CHANGE_THRESHOLD)
        min_action_interval = config.get(CONF_MIN_ACTION_INTERVAL, DEFAULT_MIN_ACTION_INTERVAL)
        self.sun_facing_tolerance = config.get(CONF_SUN_FACING_TOLERANCE, DEFAULT_SUN_FACING_TOLERANCE)
        self.sun_altitude_threshold = config.get(CONF_SUN_ALTITUDE_THRESHOLD, DEFAULT_SUN_ALTITUDE_THRESHOLD)

        # Strategy configuration
        strategy = config.get(CONF_STRATEGY, DEFAULT_STRATEGY)
        hybrid_schedule = config.get(CONF_HYBRID_SCHEDULE)

        # Sunrise/Sunset actions
        self.sunrise_action = config.get(CONF_SUNRISE_ACTION)
        self.sunset_action = config.get(CONF_SUNSET_ACTION)

        # Initialize components
        self.solar_calculator = SolarCalculator(
            latitude=latitude,
            longitude=longitude,
            elevation_m=elevation,
            timezone=timezone,
        )

        self.blind_controller = BlindController(
            window_config=window_config,
            change_threshold=change_threshold,
            min_action_interval=min_action_interval,
        )

        self.strategy_engine = StrategyEngine(
            blind_controller=self.blind_controller,
            default_strategy=strategy,
            hybrid_schedule=hybrid_schedule,
        )

        # Update interval
        update_interval = config.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry_id}",
            update_interval=timedelta(seconds=update_interval),
        )

        _LOGGER.info(
            "Coordinator initialized for %s (lat: %s, lon: %s, window: %s°)",
            self.blind_entity_id,
            latitude,
            longitude,
            window_azimuth,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from solar calculator and calculate recommendations.

        Returns:
            Dictionary with all solar and blind data
        """
        try:
            current_time = datetime.now(self.solar_calculator.tz)

            # Get solar data
            solar_data = await self.hass.async_add_executor_job(
                self.solar_calculator.get_complete_data,
                current_time,
            )

            sun_altitude = solar_data["altitude"]
            sun_azimuth = solar_data["azimuth"]

            # Check if sun is facing window
            is_sun_facing = await self.hass.async_add_executor_job(
                self.solar_calculator.is_sun_facing_window,
                self.blind_controller.window_config.azimuth,
                self.sun_facing_tolerance,
                self.sun_altitude_threshold,
                current_time,
            )

            # Check for sunrise/sunset actions first
            sunrise_state = None
            sunset_state = None

            if self.sunrise_action:
                sunrise_state = self.strategy_engine.handle_sunrise_action(
                    self.sunrise_action,
                    current_time,
                    solar_data["sunrise"],
                )

            if self.sunset_action:
                sunset_state = self.strategy_engine.handle_sunset_action(
                    self.sunset_action,
                    current_time,
                    solar_data["sunset"],
                )

            # Priority: sunrise/sunset actions > strategy-based recommendations
            if sunrise_state:
                recommended_state = sunrise_state
                should_update = True
                active_strategy = "sunrise_action"
            elif sunset_state:
                recommended_state = sunset_state
                should_update = True
                active_strategy = "sunset_action"
            else:
                # Calculate recommended state based on strategy
                (
                    recommended_state,
                    should_update,
                    active_strategy,
                ) = await self.hass.async_add_executor_job(
                    self.strategy_engine.calculate_recommended_state,
                    sun_altitude,
                    sun_azimuth,
                    is_sun_facing,
                    current_time,
                )

            # Calculate next update time
            next_update = await self.hass.async_add_executor_job(
                self.solar_calculator.get_next_update_time,
                current_time,
            )

            # Compile all data
            data = {
                # Solar data
                "sun_altitude": sun_altitude,
                "sun_azimuth": sun_azimuth,
                "solar_intensity": solar_data["solar_intensity"],
                "is_sun_facing": is_sun_facing,
                "sunrise": solar_data["sunrise"],
                "sunset": solar_data["sunset"],
                "solar_noon": solar_data["solar_noon"],
                "daylight_duration": solar_data["daylight_duration"],
                # Blind recommendations
                "recommended_position": recommended_state.position,
                "recommended_tilt": recommended_state.tilt,
                "should_update": should_update,
                # Strategy and state
                "active_strategy": active_strategy,
                "manual_override": self.strategy_engine.manual_override,
                "window_azimuth": self.blind_controller.window_config.azimuth,
                # Timing
                "calculation_time": current_time,
                "next_update": next_update,
                "last_action_time": self.blind_controller.last_action_time,
            }

            _LOGGER.debug(
                "Data updated: altitude=%.1f°, azimuth=%.1f°, facing=%s, strategy=%s, pos=%d, tilt=%d",
                sun_altitude,
                sun_azimuth,
                is_sun_facing,
                active_strategy,
                recommended_state.position,
                recommended_state.tilt,
            )

            return data

        except Exception as err:
            _LOGGER.error("Error updating solar blind adjuster data: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def set_strategy(self, strategy: str):
        """Set the control strategy.

        Args:
            strategy: Strategy name
        """
        self.strategy_engine.set_strategy(strategy)
        _LOGGER.info("Strategy set to: %s", strategy)

    def set_manual_override(self, enabled: bool):
        """Enable or disable manual override.

        Args:
            enabled: Whether to enable manual override
        """
        self.strategy_engine.set_manual_override(enabled)
        _LOGGER.info("Manual override: %s", "enabled" if enabled else "disabled")

    def record_blind_action(self, position: int, tilt: int):
        """Record that a blind action was taken.

        Args:
            position: Blind position (0-100)
            tilt: Blind tilt (0-100)
        """
        state = BlindState(position=position, tilt=tilt)
        self.blind_controller.record_action(state)
        _LOGGER.debug("Blind action recorded: pos=%d, tilt=%d", position, tilt)

    async def async_refresh_calculation(self):
        """Manually trigger a data refresh."""
        await self.async_request_refresh()
        _LOGGER.info("Manual refresh triggered")
