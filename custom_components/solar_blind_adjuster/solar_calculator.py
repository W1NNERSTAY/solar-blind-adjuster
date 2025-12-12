"""Solar position calculator for Solar Blind Adjuster."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
import math

from astral import LocationInfo
from astral.sun import sun, elevation, azimuth
import pytz

_LOGGER = logging.getLogger(__name__)


class SolarCalculator:
    """Calculate solar position and related metrics."""

    def __init__(
        self,
        latitude: float,
        longitude: float,
        elevation_m: float = 0,
        timezone: str = "UTC",
    ):
        """Initialize the solar calculator.

        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            elevation_m: Elevation in meters above sea level
            timezone: IANA timezone string
        """
        self.latitude = latitude
        self.longitude = longitude
        self.elevation_m = elevation_m
        self.timezone_str = timezone

        # Validate coordinates
        if not -90 <= latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
        if not -180 <= longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")

        # Create location info for astral
        self.location = LocationInfo(
            name="Custom",
            region="",
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
        )

        self.tz = pytz.timezone(timezone)

        _LOGGER.debug(
            "Solar calculator initialized: lat=%s, lon=%s, elev=%s, tz=%s",
            latitude,
            longitude,
            elevation_m,
            timezone,
        )

    def get_sun_position(self, dt: datetime | None = None) -> dict:
        """Get current sun position.

        Args:
            dt: DateTime to calculate for. If None, uses current time.

        Returns:
            Dictionary with sun position data:
            - altitude: Sun altitude angle in degrees (-90 to 90)
            - azimuth: Sun azimuth angle in degrees (0 to 360, North = 0)
            - is_daylight: Whether the sun is above horizon
        """
        if dt is None:
            dt = datetime.now(self.tz)
        elif dt.tzinfo is None:
            dt = self.tz.localize(dt)
        else:
            dt = dt.astimezone(self.tz)

        # Calculate sun altitude and azimuth
        sun_altitude = elevation(self.location.observer, dt)
        sun_azimuth = azimuth(self.location.observer, dt)

        return {
            "altitude": round(sun_altitude, 2),
            "azimuth": round(sun_azimuth, 2),
            "is_daylight": sun_altitude > 0,
        }

    def get_sun_times(self, date: datetime | None = None) -> dict:
        """Get sunrise, sunset, and related times.

        Args:
            date: Date to calculate for. If None, uses current date.

        Returns:
            Dictionary with sun times:
            - sunrise: Sunrise time
            - sunset: Sunset time
            - solar_noon: Solar noon time (sun at highest point)
            - daylight_duration: Hours of daylight
        """
        if date is None:
            date = datetime.now(self.tz)
        elif date.tzinfo is None:
            date = self.tz.localize(date)
        else:
            date = date.astimezone(self.tz)

        # Calculate sun times
        s = sun(self.location.observer, date=date.date(), tzinfo=self.tz)

        sunrise = s["sunrise"]
        sunset = s["sunset"]
        solar_noon = s["noon"]

        # Calculate daylight duration
        daylight_duration = (sunset - sunrise).total_seconds() / 3600

        return {
            "sunrise": sunrise,
            "sunset": sunset,
            "solar_noon": solar_noon,
            "daylight_duration": round(daylight_duration, 2),
        }

    def get_solar_intensity(self, dt: datetime | None = None) -> float:
        """Calculate relative solar intensity (0-100).

        This is a simplified calculation based on sun altitude.
        Real solar intensity depends on many factors (atmosphere, clouds, etc.)

        Args:
            dt: DateTime to calculate for. If None, uses current time.

        Returns:
            Relative solar intensity as percentage (0-100)
        """
        position = self.get_sun_position(dt)
        altitude = position["altitude"]

        # Below horizon = 0
        if altitude <= 0:
            return 0.0

        # Maximum intensity at 90 degrees (sun directly overhead)
        # Use sine function for more realistic intensity curve
        intensity = math.sin(math.radians(altitude)) * 100

        return round(max(0, min(100, intensity)), 2)

    def is_sun_facing_window(
        self,
        window_azimuth: float,
        tolerance: float = 45,
        min_altitude: float = 15,
        dt: datetime | None = None,
    ) -> bool:
        """Check if sun is facing the window.

        Args:
            window_azimuth: Direction window faces (0-360, North = 0)
            tolerance: Acceptable angle difference in degrees (default 45)
            min_altitude: Minimum sun altitude to consider (default 15 degrees)
            dt: DateTime to calculate for. If None, uses current time.

        Returns:
            True if sun is facing the window within tolerance
        """
        position = self.get_sun_position(dt)
        sun_altitude = position["altitude"]
        sun_azimuth = position["azimuth"]

        # Sun must be above minimum altitude
        if sun_altitude < min_altitude:
            return False

        # Calculate angle difference (accounting for 360-degree wrap)
        angle_diff = abs(sun_azimuth - window_azimuth)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff

        return angle_diff <= tolerance

    def get_next_update_time(
        self,
        dt: datetime | None = None,
        normal_interval: int = 300,
        sunrise_sunset_interval: int = 60,
        sunrise_sunset_window: int = 3600,
    ) -> datetime:
        """Calculate when the next update should occur.

        Updates more frequently around sunrise/sunset for smoother transitions.

        Args:
            dt: Current datetime. If None, uses current time.
            normal_interval: Normal update interval in seconds (default 300 = 5 min)
            sunrise_sunset_interval: Interval near sunrise/sunset in seconds (default 60 = 1 min)
            sunrise_sunset_window: Time window around sunrise/sunset in seconds (default 3600 = 1 hour)

        Returns:
            DateTime for next update
        """
        if dt is None:
            dt = datetime.now(self.tz)
        elif dt.tzinfo is None:
            dt = self.tz.localize(dt)
        else:
            dt = dt.astimezone(self.tz)

        sun_times = self.get_sun_times(dt)
        sunrise = sun_times["sunrise"]
        sunset = sun_times["sunset"]

        # Check if we're near sunrise or sunset
        time_to_sunrise = abs((dt - sunrise).total_seconds())
        time_to_sunset = abs((dt - sunset).total_seconds())

        if time_to_sunrise <= sunrise_sunset_window or time_to_sunset <= sunrise_sunset_window:
            interval = sunrise_sunset_interval
        else:
            interval = normal_interval

        next_update = dt + timedelta(seconds=interval)

        _LOGGER.debug(
            "Next update in %s seconds at %s",
            interval,
            next_update.isoformat(),
        )

        return next_update

    def get_complete_data(self, dt: datetime | None = None) -> dict:
        """Get all solar data in one call.

        Args:
            dt: DateTime to calculate for. If None, uses current time.

        Returns:
            Dictionary with all solar data
        """
        if dt is None:
            dt = datetime.now(self.tz)

        position = self.get_sun_position(dt)
        times = self.get_sun_times(dt)
        intensity = self.get_solar_intensity(dt)

        return {
            **position,
            **times,
            "solar_intensity": intensity,
            "calculation_time": dt,
        }
