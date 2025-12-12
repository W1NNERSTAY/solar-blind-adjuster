"""Strategy engine for Solar Blind Adjuster."""
from __future__ import annotations

from datetime import datetime, time, timedelta
import logging
from typing import Optional

from .blind_controller import BlindController, BlindState
from .const import (
    STRATEGY_MAXIMIZE_LIGHT,
    STRATEGY_BLOCK_LIGHT,
    STRATEGY_HYBRID,
    STRATEGY_MANUAL,
)

_LOGGER = logging.getLogger(__name__)


class HybridScheduleEntry:
    """Represents a time-based strategy schedule entry."""

    def __init__(self, start_time: time, end_time: time, strategy: str):
        """Initialize schedule entry.

        Args:
            start_time: Start time for this strategy
            end_time: End time for this strategy
            strategy: Strategy to use during this time
        """
        self.start_time = start_time
        self.end_time = end_time
        self.strategy = strategy

    def is_active(self, current_time: time) -> bool:
        """Check if this schedule entry is active at the given time.

        Args:
            current_time: Time to check

        Returns:
            True if this entry is active
        """
        if self.start_time <= self.end_time:
            # Normal case: e.g., 09:00 - 17:00
            return self.start_time <= current_time <= self.end_time
        else:
            # Spans midnight: e.g., 22:00 - 06:00
            return current_time >= self.start_time or current_time <= self.end_time


class StrategyEngine:
    """Manages strategy selection and execution."""

    def __init__(
        self,
        blind_controller: BlindController,
        default_strategy: str = STRATEGY_BLOCK_LIGHT,
        hybrid_schedule: Optional[list[dict]] = None,
    ):
        """Initialize the strategy engine.

        Args:
            blind_controller: Blind controller instance
            default_strategy: Default strategy to use
            hybrid_schedule: Schedule for hybrid mode (list of dicts with start_time, end_time, strategy)
        """
        self.blind_controller = blind_controller
        self.default_strategy = default_strategy
        self.current_strategy = default_strategy
        self.manual_override = False
        self.hybrid_schedule: list[HybridScheduleEntry] = []

        # Parse hybrid schedule if provided
        if hybrid_schedule:
            self._parse_hybrid_schedule(hybrid_schedule)

        _LOGGER.debug(
            "Strategy engine initialized: default=%s, hybrid_entries=%s",
            default_strategy,
            len(self.hybrid_schedule),
        )

    def _parse_hybrid_schedule(self, schedule: list[dict]):
        """Parse hybrid schedule from configuration.

        Args:
            schedule: List of schedule entries
        """
        for entry in schedule:
            try:
                start_time = self._parse_time(entry["start_time"])
                end_time = self._parse_time(entry["end_time"])
                strategy = entry["strategy"]

                if strategy not in [STRATEGY_MAXIMIZE_LIGHT, STRATEGY_BLOCK_LIGHT]:
                    _LOGGER.warning(
                        "Invalid strategy '%s' in hybrid schedule, skipping",
                        strategy,
                    )
                    continue

                self.hybrid_schedule.append(
                    HybridScheduleEntry(start_time, end_time, strategy)
                )
                _LOGGER.debug(
                    "Added hybrid schedule: %s-%s: %s",
                    start_time,
                    end_time,
                    strategy,
                )
            except (KeyError, ValueError) as e:
                _LOGGER.error("Error parsing hybrid schedule entry: %s", e)

    def _parse_time(self, time_str: str) -> time:
        """Parse time string in HH:MM format.

        Args:
            time_str: Time string (e.g., "09:00")

        Returns:
            time object
        """
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid time format: {time_str}")
        return time(hour=int(parts[0]), minute=int(parts[1]))

    def set_strategy(self, strategy: str):
        """Set the current strategy.

        Args:
            strategy: Strategy to set
        """
        if strategy not in [
            STRATEGY_MAXIMIZE_LIGHT,
            STRATEGY_BLOCK_LIGHT,
            STRATEGY_HYBRID,
            STRATEGY_MANUAL,
        ]:
            _LOGGER.warning("Invalid strategy '%s', ignoring", strategy)
            return

        self.current_strategy = strategy
        _LOGGER.info("Strategy changed to: %s", strategy)

    def set_manual_override(self, enabled: bool):
        """Enable or disable manual override.

        When manual override is enabled, automatic control is disabled.

        Args:
            enabled: Whether to enable manual override
        """
        self.manual_override = enabled
        _LOGGER.info("Manual override: %s", "enabled" if enabled else "disabled")

    def get_active_strategy(self, current_time: datetime | None = None) -> str:
        """Get the currently active strategy.

        Takes into account:
        - Manual override (highest priority)
        - Hybrid schedule
        - Default strategy

        Args:
            current_time: Current time (None = now)

        Returns:
            Active strategy name
        """
        # Manual override has highest priority
        if self.manual_override:
            return STRATEGY_MANUAL

        # If current strategy is not hybrid, return it
        if self.current_strategy != STRATEGY_HYBRID:
            return self.current_strategy

        # Hybrid mode: check schedule
        if current_time is None:
            current_time = datetime.now()

        current_time_only = current_time.time()

        for entry in self.hybrid_schedule:
            if entry.is_active(current_time_only):
                _LOGGER.debug(
                    "Hybrid schedule active: %s at %s",
                    entry.strategy,
                    current_time_only,
                )
                return entry.strategy

        # No schedule match, use default
        _LOGGER.debug("No hybrid schedule match, using default: %s", self.default_strategy)
        return self.default_strategy

    def calculate_recommended_state(
        self,
        sun_altitude: float,
        sun_azimuth: float,
        is_sun_facing: bool,
        current_time: datetime | None = None,
    ) -> tuple[BlindState, bool, str]:
        """Calculate recommended blind state based on active strategy.

        Args:
            sun_altitude: Sun altitude angle in degrees
            sun_azimuth: Sun azimuth angle in degrees
            is_sun_facing: Whether sun is facing the window
            current_time: Current time (None = now)

        Returns:
            Tuple of (recommended_state, should_update, active_strategy)
        """
        active_strategy = self.get_active_strategy(current_time)

        # Get recommendation from blind controller
        recommended_state, should_update = self.blind_controller.get_recommended_state(
            sun_altitude=sun_altitude,
            sun_azimuth=sun_azimuth,
            is_sun_facing=is_sun_facing,
            strategy=active_strategy,
            current_time=current_time,
        )

        _LOGGER.debug(
            "Recommendation: strategy=%s, position=%s, tilt=%s, should_update=%s",
            active_strategy,
            recommended_state.position,
            recommended_state.tilt,
            should_update,
        )

        return recommended_state, should_update, active_strategy

    def handle_sunrise_action(
        self,
        sunrise_config: Optional[dict],
        current_time: datetime,
        sunrise_time: datetime,
    ) -> Optional[BlindState]:
        """Handle sunrise action if configured.

        Args:
            sunrise_config: Sunrise configuration (enabled, offset, position, tilt)
            current_time: Current time
            sunrise_time: Calculated sunrise time

        Returns:
            BlindState to apply, or None if no action needed
        """
        if not sunrise_config or not sunrise_config.get("enabled", False):
            return None

        offset_minutes = sunrise_config.get("offset", 0)
        trigger_time = sunrise_time + timedelta(minutes=offset_minutes)

        # Check if we should trigger (within 1 minute of trigger time)
        time_diff = abs((current_time - trigger_time).total_seconds())
        if time_diff > 60:
            return None

        position = sunrise_config.get("position", 100)
        tilt = sunrise_config.get("tilt", 100)

        _LOGGER.info(
            "Sunrise action triggered: position=%s, tilt=%s",
            position,
            tilt,
        )

        return BlindState(position=position, tilt=tilt)

    def handle_sunset_action(
        self,
        sunset_config: Optional[dict],
        current_time: datetime,
        sunset_time: datetime,
    ) -> Optional[BlindState]:
        """Handle sunset action if configured.

        Args:
            sunset_config: Sunset configuration (enabled, offset, position, tilt)
            current_time: Current time
            sunset_time: Calculated sunset time

        Returns:
            BlindState to apply, or None if no action needed
        """
        if not sunset_config or not sunset_config.get("enabled", False):
            return None

        offset_minutes = sunset_config.get("offset", 0)
        trigger_time = sunset_time + timedelta(minutes=offset_minutes)

        # Check if we should trigger (within 1 minute of trigger time)
        time_diff = abs((current_time - trigger_time).total_seconds())
        if time_diff > 60:
            return None

        position = sunset_config.get("position", 0)
        tilt = sunset_config.get("tilt", 0)

        _LOGGER.info(
            "Sunset action triggered: position=%s, tilt=%s",
            position,
            tilt,
        )

        return BlindState(position=position, tilt=tilt)
