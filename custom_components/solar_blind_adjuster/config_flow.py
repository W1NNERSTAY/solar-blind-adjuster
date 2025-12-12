"""Config flow for Solar Blind Adjuster integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_BLIND_ENTITY_ID,
    CONF_CHANGE_THRESHOLD,
    CONF_ELEVATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MIN_ACTION_INTERVAL,
    CONF_POSITION_LIMITS,
    CONF_STRATEGY,
    CONF_SUN_ALTITUDE_THRESHOLD,
    CONF_SUN_FACING_TOLERANCE,
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
    STRATEGIES,
)

_LOGGER = logging.getLogger(__name__)


class SolarBlindAdjusterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solar Blind Adjuster."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.data = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step - basic information."""
        errors = {}

        if user_input is not None:
            # Validate blind entity exists
            blind_entity = user_input[CONF_BLIND_ENTITY_ID]
            if not self.hass.states.get(blind_entity):
                errors[CONF_BLIND_ENTITY_ID] = "entity_not_found"
            else:
                self.data.update(user_input)
                return await self.async_step_location()

        # Get list of cover entities for selection
        cover_entities = [
            entity_id
            for entity_id in self.hass.states.async_entity_ids("cover")
        ]

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Solar Blind Adjuster"): str,
                vol.Required(CONF_BLIND_ENTITY_ID): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="cover")
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "name": "Solar Blind Adjuster",
            },
        )

    async def async_step_location(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle location configuration step."""
        errors = {}

        if user_input is not None:
            # Validate coordinates
            latitude = user_input.get(CONF_LATITUDE, self.hass.config.latitude)
            longitude = user_input.get(CONF_LONGITUDE, self.hass.config.longitude)

            if not -90 <= latitude <= 90:
                errors[CONF_LATITUDE] = "invalid_latitude"
            elif not -180 <= longitude <= 180:
                errors[CONF_LONGITUDE] = "invalid_longitude"
            elif not 0 <= user_input[CONF_WINDOW_AZIMUTH] <= 360:
                errors[CONF_WINDOW_AZIMUTH] = "invalid_azimuth"
            else:
                self.data.update(user_input)
                return await self.async_step_strategy()

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_LATITUDE,
                    default=self.hass.config.latitude,
                ): cv.latitude,
                vol.Optional(
                    CONF_LONGITUDE,
                    default=self.hass.config.longitude,
                ): cv.longitude,
                vol.Optional(
                    CONF_ELEVATION,
                    default=self.hass.config.elevation or 0,
                ): int,
                vol.Required(CONF_WINDOW_AZIMUTH): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=0, max=360),
                ),
            }
        )

        return self.async_show_form(
            step_id="location",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "latitude": str(self.hass.config.latitude),
                "longitude": str(self.hass.config.longitude),
            },
        )

    async def async_step_strategy(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle strategy selection step."""
        if user_input is not None:
            self.data.update(user_input)
            return await self.async_step_advanced()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_STRATEGY, default=DEFAULT_STRATEGY): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(
                                value="maximize_light",
                                label="Maximize Light - 빛 최대 유입",
                            ),
                            selector.SelectOptionDict(
                                value="block_light",
                                label="Block Light - 직사광 차단",
                            ),
                            selector.SelectOptionDict(
                                value="hybrid",
                                label="Hybrid - 시간대별 자동 전환",
                            ),
                            selector.SelectOptionDict(
                                value="manual",
                                label="Manual - 수동 모드",
                            ),
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="strategy",
            data_schema=data_schema,
            description_placeholders={
                "strategy_info": "Choose control strategy",
            },
        )

    async def async_step_advanced(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle advanced configuration step (optional)."""
        if user_input is not None:
            # Process limits
            if user_input.get("position_min") is not None:
                self.data[CONF_POSITION_LIMITS] = {
                    "min": user_input.pop("position_min"),
                    "max": user_input.pop("position_max"),
                }
            if user_input.get("tilt_min") is not None:
                self.data[CONF_TILT_LIMITS] = {
                    "min": user_input.pop("tilt_min"),
                    "max": user_input.pop("tilt_max"),
                }

            self.data.update(user_input)

            # Create config entry
            return self.async_create_entry(
                title=self.data[CONF_NAME],
                data=self.data,
            )

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=DEFAULT_UPDATE_INTERVAL,
                ): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
                vol.Optional(
                    CONF_CHANGE_THRESHOLD,
                    default=DEFAULT_CHANGE_THRESHOLD,
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=50)),
                vol.Optional(
                    CONF_MIN_ACTION_INTERVAL,
                    default=DEFAULT_MIN_ACTION_INTERVAL,
                ): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
                vol.Optional(
                    CONF_SUN_FACING_TOLERANCE,
                    default=DEFAULT_SUN_FACING_TOLERANCE,
                ): vol.All(vol.Coerce(int), vol.Range(min=15, max=90)),
                vol.Optional(
                    CONF_SUN_ALTITUDE_THRESHOLD,
                    default=DEFAULT_SUN_ALTITUDE_THRESHOLD,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=45)),
                vol.Optional(
                    "position_min",
                    default=DEFAULT_POSITION_MIN,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                vol.Optional(
                    "position_max",
                    default=DEFAULT_POSITION_MAX,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                vol.Optional(
                    "tilt_min",
                    default=DEFAULT_TILT_MIN,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                vol.Optional(
                    "tilt_max",
                    default=DEFAULT_TILT_MAX,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
            }
        )

        return self.async_show_form(
            step_id="advanced",
            data_schema=data_schema,
            description_placeholders={
                "advanced_info": "Advanced settings (optional)",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SolarBlindAdjusterOptionsFlow:
        """Get the options flow for this handler."""
        return SolarBlindAdjusterOptionsFlow(config_entry)


class SolarBlindAdjusterOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Solar Blind Adjuster."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_strategy = self.config_entry.data.get(CONF_STRATEGY, DEFAULT_STRATEGY)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_STRATEGY,
                    default=current_strategy,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(
                                value="maximize_light",
                                label="Maximize Light",
                            ),
                            selector.SelectOptionDict(
                                value="block_light",
                                label="Block Light",
                            ),
                            selector.SelectOptionDict(
                                value="hybrid",
                                label="Hybrid",
                            ),
                            selector.SelectOptionDict(
                                value="manual",
                                label="Manual",
                            ),
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
