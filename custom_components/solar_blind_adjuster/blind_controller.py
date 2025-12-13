"""Blind controller for Solar Blind Adjuster."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Optional

_LOGGER = logging.getLogger(__name__)


@dataclass
class BlindState:
    """Represents the state of a blind."""

    position: int  # 0-100, 0=fully closed, 100=fully open
    tilt: int  # 0-100, 0=fully closed, 100=fully open

    def __post_init__(self):
        """Validate blind state values."""
        if not 0 <= self.position <= 100:
            raise ValueError(f"Position must be 0-100, got {self.position}")
        if not 0 <= self.tilt <= 100:
            raise ValueError(f"Tilt must be 0-100, got {self.tilt}")


@dataclass
class WindowConfig:
    """Configuration for a window."""

    azimuth: float  # Direction window faces (0-360, North = 0)
    tilt_offset: float = 0  # Slat angle correction (-45 to 45 degrees)
    position_min: int = 0  # Minimum position limit
    position_max: int = 100  # Maximum position limit
    tilt_min: int = 0  # Minimum tilt limit
    tilt_max: int = 100  # Maximum tilt limit

    def __post_init__(self):
        """Validate window config values."""
        if not 0 <= self.azimuth <= 360:
            raise ValueError(f"Azimuth must be 0-360, got {self.azimuth}")
        if not -45 <= self.tilt_offset <= 45:
            raise ValueError(f"Tilt offset must be -45 to 45, got {self.tilt_offset}")
        if not 0 <= self.position_min <= 100:
            raise ValueError(f"Position min must be 0-100, got {self.position_min}")
        if not 0 <= self.position_max <= 100:
            raise ValueError(f"Position max must be 0-100, got {self.position_max}")
        if self.position_min > self.position_max:
            raise ValueError("Position min cannot be greater than position max")
        if not 0 <= self.tilt_min <= 100:
            raise ValueError(f"Tilt min must be 0-100, got {self.tilt_min}")
        if not 0 <= self.tilt_max <= 100:
            raise ValueError(f"Tilt max must be 0-100, got {self.tilt_max}")
        if self.tilt_min > self.tilt_max:
            raise ValueError("Tilt min cannot be greater than tilt max")


class BlindController:
    """Controls blind position and tilt based on solar data."""

    def __init__(
        self,
        window_config: WindowConfig,
        change_threshold: int = 5,
        min_action_interval: int = 300,
    ):
        """Initialize the blind controller.

        Args:
            window_config: Configuration for the window
            change_threshold: Minimum change percentage to trigger update (default 5%)
            min_action_interval: Minimum seconds between actions (default 300 = 5 min)
        """
        self.window_config = window_config
        self.change_threshold = change_threshold
        self.min_action_interval = min_action_interval
        self.last_action_time: Optional[datetime] = None
        self.last_state: Optional[BlindState] = None

        _LOGGER.debug(
            "Blind controller initialized: window_azimuth=%s, change_threshold=%s, min_interval=%s",
            window_config.azimuth,
            change_threshold,
            min_action_interval,
        )

    def calculate_target_state(
        self,
        sun_altitude: float,
        sun_azimuth: float,
        is_sun_facing: bool,
        strategy: str,
    ) -> BlindState:
        """Calculate target blind state based on solar position and strategy.

        Args:
            sun_altitude: Sun altitude angle in degrees
            sun_azimuth: Sun azimuth angle in degrees
            is_sun_facing: Whether sun is facing the window
            strategy: Control strategy ('maximize_light', 'block_light', 'hybrid', 'manual')

        Returns:
            Target blind state
        """
        if strategy == "maximize_light":
            return self._calculate_maximize_light(sun_altitude, sun_azimuth, is_sun_facing)
        elif strategy == "block_light":
            return self._calculate_block_light(sun_altitude, sun_azimuth, is_sun_facing)
        elif strategy == "hybrid":
            # Hybrid is handled by strategy engine
            # Default to block_light if called directly
            return self._calculate_block_light(sun_altitude, sun_azimuth, is_sun_facing)
        elif strategy == "manual":
            # Manual mode: maintain current state or return neutral state
            if self.last_state:
                return self.last_state
            return BlindState(position=50, tilt=50)
        else:
            _LOGGER.warning("Unknown strategy '%s', using block_light", strategy)
            return self._calculate_block_light(sun_altitude, sun_azimuth, is_sun_facing)

    def _calculate_maximize_light(
        self,
        sun_altitude: float,
        sun_azimuth: float,
        is_sun_facing: bool,
    ) -> BlindState:
        """Calculate blind state to maximize light entry.

        Args:
            sun_altitude: Sun altitude angle in degrees
            sun_azimuth: Sun azimuth angle in degrees
            is_sun_facing: Whether sun is facing the window

        Returns:
            Target blind state for maximum light
        """
        if is_sun_facing and sun_altitude > 0:
            # Direct sunlight: fully open, tilt for optimal light entry
            position = 100
            # Tilt based on sun altitude for optimal light entry
            # Higher altitude = more horizontal slats
            tilt = min(100, int(50 + sun_altitude * 0.5))
        else:
            # No direct sunlight: partially open for indirect light
            position = 75
            tilt = 75

        return self._apply_limits(BlindState(position=position, tilt=tilt))

    def _calculate_block_light(
        self,
        sun_altitude: float,
        sun_azimuth: float,
        is_sun_facing: bool,
    ) -> BlindState:
        """Calculate blind state to block direct sunlight.

        Args:
            sun_altitude: Sun altitude angle in degrees
            sun_azimuth: Sun azimuth angle in degrees
            is_sun_facing: Whether sun is facing the window

        Returns:
            Target blind state for blocking light
        """
        if is_sun_facing and sun_altitude > 0:
            # Direct sunlight: partially close and angle to block
            # Higher altitude = more blocking needed
            position = max(30, int(100 - sun_altitude * 0.8))
            # Tilt to block direct rays while allowing some light
            tilt = max(20, int(100 - sun_altitude * 1.2))
        else:
            # No direct sunlight: open for indirect light and view
            position = 100
            tilt = 100

        return self._apply_limits(BlindState(position=position, tilt=tilt))

    def _apply_limits(self, state: BlindState) -> BlindState:
        """Apply window configuration limits to blind state.

        Args:
            state: Desired blind state

        Returns:
            Blind state with limits applied
        """
        position = max(
            self.window_config.position_min,
            min(self.window_config.position_max, state.position)
        )
        tilt = max(
            self.window_config.tilt_min,
            min(self.window_config.tilt_max, state.tilt)
        )

        return BlindState(position=position, tilt=tilt)

    def should_update(
        self,
        target_state: BlindState,
        current_time: datetime | None = None,
    ) -> bool:
        """Determine if blind should be updated.

        Checks:
        1. If change exceeds threshold
        2. If minimum interval has passed since last action

        Args:
            target_state: Desired blind state
            current_time: Current time (None = now)

        Returns:
            True if blind should be updated
        """
        if current_time is None:
            current_time = datetime.now()

        # First update always goes through
        if self.last_state is None or self.last_action_time is None:
            return True

        # Check minimum interval
        time_since_last = (current_time - self.last_action_time).total_seconds()
        if time_since_last < self.min_action_interval:
            _LOGGER.debug(
                "Skipping update: only %s seconds since last action (min: %s)",
                time_since_last,
                self.min_action_interval,
            )
            return False

        # Check change threshold
        position_change = abs(target_state.position - self.last_state.position)
        tilt_change = abs(target_state.tilt - self.last_state.tilt)

        if position_change < self.change_threshold and tilt_change < self.change_threshold:
            _LOGGER.debug(
                "Skipping update: changes (pos: %s, tilt: %s) below threshold (%s)",
                position_change,
                tilt_change,
                self.change_threshold,
            )
            return False

        return True

    def record_action(
        self,
        state: BlindState,
        action_time: datetime | None = None,
    ):
        """Record that an action was taken.

        Args:
            state: Blind state that was set
            action_time: Time of action (None = now)
        """
        if action_time is None:
            action_time = datetime.now()

        self.last_state = state
        self.last_action_time = action_time

        _LOGGER.debug(
            "Recorded action at %s: position=%s, tilt=%s",
            action_time.isoformat(),
            state.position,
            state.tilt,
        )

    def get_recommended_state(
        self,
        sun_altitude: float,
        sun_azimuth: float,
        is_sun_facing: bool,
        strategy: str,
        current_time: datetime | None = None,
    ) -> tuple[BlindState, bool]:
        """Get recommended blind state and whether to update.

        This is the main method to call for getting blind recommendations.

        Args:
            sun_altitude: Sun altitude angle in degrees
            sun_azimuth: Sun azimuth angle in degrees
            is_sun_facing: Whether sun is facing the window
            strategy: Control strategy
            current_time: Current time (None = now)

        Returns:
            Tuple of (recommended_state, should_update)
        """
        target_state = self.calculate_target_state(
            sun_altitude,
            sun_azimuth,
            is_sun_facing,
            strategy,
        )

        should_update = self.should_update(target_state, current_time)

        return target_state, should_update
