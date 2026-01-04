"""Number platform for Parmair MAC integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REG_AWAY_SPEED,
    REG_BOOST_SETTING,
    REG_BOOST_TIMER,
    REG_EXHAUST_TEMP_SETPOINT,
    REG_FILTER_INTERVAL,
    REG_HOME_SPEED,
    REG_OVERPRESSURE_TIMER,
    REG_SUMMER_MODE_TEMP_LIMIT,
    REG_SUPPLY_TEMP_SETPOINT,
)
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Parmair number platform."""
    coordinator: ParmairCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NumberEntity] = [
        ParmairSpeedPresetNumber(coordinator, entry, REG_HOME_SPEED, "Home Speed Preset"),
        ParmairSpeedPresetNumber(coordinator, entry, REG_AWAY_SPEED, "Away Speed Preset"),
        ParmairSpeedPresetNumber(coordinator, entry, REG_BOOST_SETTING, "Boost Speed Preset"),
        ParmairTemperatureSetpointNumber(
            coordinator, entry, REG_EXHAUST_TEMP_SETPOINT, "Exhaust Temperature Setpoint"
        ),
        ParmairTemperatureSetpointNumber(
            coordinator, entry, REG_SUPPLY_TEMP_SETPOINT, "Supply Temperature Setpoint"
        ),
        ParmairTemperatureSetpointNumber(
            coordinator, entry, REG_SUMMER_MODE_TEMP_LIMIT, "Summer Mode Temperature Limit"
        ),
        ParmairFilterIntervalNumber(
            coordinator, entry, REG_FILTER_INTERVAL, "Filter Change Interval"
        ),
        ParmairTimerNumber(
            coordinator, entry, REG_BOOST_TIMER, "Boost Timer", "mdi:timer", "Set boost mode timer in minutes"
        ),
        ParmairTimerNumber(
            coordinator, entry, REG_OVERPRESSURE_TIMER, "Overpressure Timer", "mdi:timer", "Set overpressure mode timer in minutes"
        ),
    ]

    async_add_entities(entities)


class ParmairNumberEntity(CoordinatorEntity[ParmairCoordinator], NumberEntity):
    """Base class for Parmair number entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get(self._data_key)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        try:
            await self.coordinator.async_write_register(self._data_key, int(value))
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set %s to %s: %s", self._data_key, value, ex)
            raise


class ParmairSpeedPresetNumber(ParmairNumberEntity):
    """Number entity for fan speed presets (0-4)."""

    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0
    _attr_native_max_value = 4
    _attr_native_step = 1
    _attr_icon = "mdi:fan"

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize speed preset number."""
        super().__init__(coordinator, entry, data_key, name)
        
        # Adjust boost setting range (2-4 per documentation)
        if data_key == REG_BOOST_SETTING:
            self._attr_native_min_value = 2


class ParmairTemperatureSetpointNumber(ParmairNumberEntity):
    """Number entity for temperature setpoints."""

    _attr_mode = NumberMode.BOX
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = "temperature"
    _attr_icon = "mdi:thermometer"

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize temperature setpoint number."""
        super().__init__(coordinator, entry, data_key, name)
        
        # Set appropriate ranges based on register
        if data_key == REG_EXHAUST_TEMP_SETPOINT:
            self._attr_native_min_value = 18.0
            self._attr_native_max_value = 26.0
            self._attr_native_step = 0.5
        elif data_key == REG_SUPPLY_TEMP_SETPOINT:
            self._attr_native_min_value = 15.0
            self._attr_native_max_value = 25.0
            self._attr_native_step = 0.5
        elif data_key == REG_SUMMER_MODE_TEMP_LIMIT:
            self._attr_native_min_value = 15.0
            self._attr_native_max_value = 30.0
            self._attr_native_step = 0.5


class ParmairFilterIntervalNumber(ParmairNumberEntity):
    """Number entity for filter change interval (months)."""

    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0
    _attr_native_max_value = 2
    _attr_native_step = 1
    _attr_icon = "mdi:air-filter"
    _attr_native_unit_of_measurement = "setting"

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize filter interval number."""
        super().__init__(coordinator, entry, data_key, name)


class ParmairTimerNumber(ParmairNumberEntity):
    """Number entity for boost/overpressure timers (minutes)."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 300
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "min"

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        icon: str,
        description: str,
    ) -> None:
        """Initialize timer number."""
        super().__init__(coordinator, entry, data_key, name)
        self._attr_icon = icon

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        attrs = super().extra_state_attributes if hasattr(super(), 'extra_state_attributes') else {}
        value = self.native_value
        if value is not None:
            interval_map = {0: "3 months", 1: "4 months", 2: "6 months"}
            attrs["interval_description"] = interval_map.get(int(value), "Unknown")
        return attrs
