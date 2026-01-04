"""Switch platform for Parmair MAC integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REG_BOOST_STATE,
    REG_CONTROL_STATE,
    REG_HEATER_ENABLE,
    REG_OVERPRESSURE_STATE,
    REG_SUMMER_MODE,
    REG_TIME_PROGRAM_ENABLE,
)
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Parmair switch platform."""
    coordinator: ParmairCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SwitchEntity] = [
        ParmairSwitch(
            coordinator,
            entry,
            REG_SUMMER_MODE,
            "Summer Mode",
            "mdi:weather-sunny",
            "Enables heat recovery summer operation mode",
        ),
        ParmairSwitch(
            coordinator,
            entry,
            REG_TIME_PROGRAM_ENABLE,
            "Time Program",
            "mdi:clock-outline",
            "Enables weekly time program control",
        ),
        ParmairSwitch(
            coordinator,
            entry,
            REG_HEATER_ENABLE,
            "Post Heater",
            "mdi:radiator",
            "Enables post-heating element",
        ),
        ParmairBoostSwitch(
            coordinator,
            entry,
            "Boost Mode",
            "mdi:fan-speed-3",
            "Activates boost ventilation mode",
        ),
        ParmairOverpressureSwitch(
            coordinator,
            entry,
            "Overpressure Mode",
            "mdi:gauge",
            "Activates overpressure mode",
        ),
    ]

    async_add_entities(entities)


class ParmairSwitch(CoordinatorEntity[ParmairCoordinator], SwitchEntity):
    """Representation of a Parmair switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        icon: str,
        description: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_device_info = coordinator.device_info
        self._attr_entity_registry_enabled_default = True

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        value = self.coordinator.data.get(self._data_key)
        return value == 1 if value is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            await self.coordinator.async_write_register(self._data_key, 1)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to turn on %s: %s", self._data_key, ex)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            await self.coordinator.async_write_register(self._data_key, 0)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to turn off %s: %s", self._data_key, ex)
            raise


class ParmairBoostSwitch(CoordinatorEntity[ParmairCoordinator], SwitchEntity):
    """Representation of a Parmair boost mode switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        name: str,
        icon: str,
        description: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_boost_mode"
        self._attr_device_info = coordinator.device_info
        self._attr_entity_registry_enabled_default = True

    @property
    def is_on(self) -> bool | None:
        """Return true if boost mode is active."""
        # Check if control state is 3 (boost) or 7 (boost via time program)
        control_state = self.coordinator.data.get(REG_CONTROL_STATE)
        boost_state = self.coordinator.data.get(REG_BOOST_STATE)
        return control_state in (3, 7) or boost_state == 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Activate boost mode."""
        try:
            await self.coordinator.async_write_register(REG_CONTROL_STATE, 3)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to activate boost mode: %s", ex)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Deactivate boost mode (return to home mode)."""
        try:
            await self.coordinator.async_write_register(REG_CONTROL_STATE, 2)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to deactivate boost mode: %s", ex)
            raise


class ParmairOverpressureSwitch(CoordinatorEntity[ParmairCoordinator], SwitchEntity):
    """Representation of a Parmair overpressure mode switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        name: str,
        icon: str,
        description: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_overpressure_mode"
        self._attr_device_info = coordinator.device_info
        self._attr_entity_registry_enabled_default = True

    @property
    def is_on(self) -> bool | None:
        """Return true if overpressure mode is active."""
        # Check if control state is 4 (overpressure) or 8 (overpressure via time program)
        control_state = self.coordinator.data.get(REG_CONTROL_STATE)
        overp_state = self.coordinator.data.get(REG_OVERPRESSURE_STATE)
        return control_state in (4, 8) or overp_state == 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Activate overpressure mode."""
        try:
            await self.coordinator.async_write_register(REG_CONTROL_STATE, 4)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to activate overpressure mode: %s", ex)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Deactivate overpressure mode (return to home mode)."""
        try:
            await self.coordinator.async_write_register(REG_CONTROL_STATE, 2)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to deactivate overpressure mode: %s", ex)
            raise
