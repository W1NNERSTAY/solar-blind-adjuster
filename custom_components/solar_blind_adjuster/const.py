"""Constants for the Solar Blind Adjuster integration."""

# Domain
DOMAIN = "solar_blind_adjuster"

# Configuration keys
CONF_BLIND_ENTITY_ID = "blind_entity_id"
CONF_BLIND_ENTITY_IDS = "blind_entity_ids"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_ELEVATION = "elevation"
CONF_WINDOW_AZIMUTH = "window_azimuth"
CONF_STRATEGY = "strategy"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_POSITION_LIMITS = "position_limits"
CONF_TILT_LIMITS = "tilt_limits"
CONF_CHANGE_THRESHOLD = "change_threshold"
CONF_MIN_ACTION_INTERVAL = "min_action_interval"
CONF_SUN_FACING_TOLERANCE = "sun_facing_tolerance"
CONF_SUN_ALTITUDE_THRESHOLD = "sun_altitude_threshold"
CONF_SUNRISE_ACTION = "sunrise_action"
CONF_SUNSET_ACTION = "sunset_action"
CONF_HYBRID_SCHEDULE = "hybrid_schedule"
CONF_DIRECTION_CHOICE = "window_direction"
CONF_CUSTOM_AZIMUTH = "custom_window_azimuth"

# Strategy types
STRATEGY_MAXIMIZE_LIGHT = "maximize_light"
STRATEGY_BLOCK_LIGHT = "block_light"
STRATEGY_HYBRID = "hybrid"
STRATEGY_MANUAL = "manual"

STRATEGIES = [
    STRATEGY_MAXIMIZE_LIGHT,
    STRATEGY_BLOCK_LIGHT,
    STRATEGY_HYBRID,
    STRATEGY_MANUAL,
]

# Default values
DEFAULT_STRATEGY = STRATEGY_BLOCK_LIGHT
DEFAULT_UPDATE_INTERVAL = 300  # 5 minutes in seconds
DEFAULT_CHANGE_THRESHOLD = 5  # 5% change threshold
DEFAULT_MIN_ACTION_INTERVAL = 300  # 5 minutes in seconds
DEFAULT_SUN_FACING_TOLERANCE = 45  # degrees
DEFAULT_SUN_ALTITUDE_THRESHOLD = 15  # degrees
DEFAULT_POSITION_MIN = 0
DEFAULT_POSITION_MAX = 100
DEFAULT_TILT_MIN = 0
DEFAULT_TILT_MAX = 100

# Sensor types
SENSOR_SUN_ALTITUDE = "sun_altitude"
SENSOR_SUN_AZIMUTH = "sun_azimuth"
SENSOR_SOLAR_INTENSITY = "solar_intensity"
SENSOR_RECOMMENDED_POSITION = "recommended_position"
SENSOR_RECOMMENDED_TILT = "recommended_tilt"
BINARY_SENSOR_SUN_FACING = "sun_facing"

# Attributes
ATTR_SUNRISE = "sunrise"
ATTR_SUNSET = "sunset"
ATTR_SOLAR_NOON = "solar_noon"
ATTR_DAYLIGHT_DURATION = "daylight_duration"
ATTR_CURRENT_STRATEGY = "current_strategy"
ATTR_MANUAL_OVERRIDE = "manual_override"
ATTR_NEXT_UPDATE = "next_update"
ATTR_WINDOW_AZIMUTH = "window_azimuth"
ATTR_LAST_ACTION_TIME = "last_action_time"
ATTR_CONTROLLED_BLINDS = "controlled_blinds"

# Services
SERVICE_UPDATE_POSITION = "update_position"
SERVICE_SET_STRATEGY = "set_strategy"
SERVICE_REFRESH_CALCULATION = "refresh_calculation"
SERVICE_RUN_SIMULATION = "run_simulation"
SERVICE_PREVIEW_TIME = "preview_time"

# Icons
ICON_SUN_ALTITUDE = "mdi:angle-acute"
ICON_SUN_AZIMUTH = "mdi:compass"
ICON_SOLAR_INTENSITY = "mdi:white-balance-sunny"
ICON_RECOMMENDED_POSITION = "mdi:window-shutter"
ICON_RECOMMENDED_TILT = "mdi:blinds"
ICON_SUN_FACING = "mdi:weather-sunny"

# Units
UNIT_DEGREES = "°"
UNIT_PERCENT = "%"
UNIT_HOURS = "h"

# Cardinal directions helper (used in config flow)
CARDINAL_DIRECTIONS = {
    "north": 0,
    "east": 90,
    "south": 180,
    "west": 270,
}
