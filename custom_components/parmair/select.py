"""Select platform for Parmair MAC integration."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REG_HEATER_TYPE,
)
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Parmair select platform."""
    coordinator: ParmairCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SelectEntity] = [
        ParmairHeaterTypeSelect(coordinator, entry, REG_HEATER_TYPE, "Heater Type"),
    ]

    async_add_entities(entities)


class ParmairHeaterTypeSelect(CoordinatorEntity[ParmairCoordinator], SelectEntity):
    """Representation of a Parmair heater type select."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:radiator"
    _attr_options = ["Water", "Electric"]

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        value = self.coordinator.data.get(self._data_key)
        if value is None:
            return None
        # 0 = Water, 1 = Electric
        return "Electric" if value == 1 else "Water"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            # Convert option to value: Water = 0, Electric = 1
            value = 1 if option == "Electric" else 0
            _LOGGER.debug(
                "Setting %s to %s (value: %s)",
                self._attr_name,
                option,
                value,
            )
            await self.coordinator.async_write_register(self._data_key, value)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set %s to %s: %s", self._attr_name, option, ex)
            raise
