"""DataUpdateCoordinator for Parmair integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    REGISTER_POWER,
    REGISTER_CONTROL_STATE,
    REGISTER_SPEED_CONTROL,
    REGISTER_FRESH_AIR_TEMP,
    REGISTER_SUPPLY_TEMP,
    REGISTER_EXHAUST_TEMP,
    REGISTER_WASTE_TEMP,
    REGISTER_EXHAUST_TEMP_SETPOINT,
    REGISTER_SUPPLY_TEMP_SETPOINT,
    REGISTER_HOME_SPEED,
    REGISTER_AWAY_SPEED,
    REGISTER_HOME_STATE,
    REGISTER_BOOST_STATE,
    REGISTER_BOOST_TIMER,
    REGISTER_HUMIDITY,
    REGISTER_CO2,
    REGISTER_ALARM_COUNT,
    REGISTER_SUM_ALARM,
)

_LOGGER = logging.getLogger(__name__)


class ParmairCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Parmair data from Modbus."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.slave_id = entry.data[CONF_SLAVE_ID]
        
        self._client = ModbusTcpClient(host=self.host, port=self.port)
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.host}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Parmair via Modbus."""
        try:
            return await self.hass.async_add_executor_job(self._read_modbus_data)
        except ModbusException as err:
            raise UpdateFailed(f"Error communicating with Parmair device: {err}") from err

    def _read_modbus_data(self) -> dict[str, Any]:
        """Read data from Modbus (runs in executor)."""
        if not self._client.connected:
            if not self._client.connect():
                raise ModbusException("Failed to connect to Modbus device")
        
        data = {}
        
        try:
            # Read power status (Register 208)
            result = self._client.read_holding_registers(
                REGISTER_POWER, 1, unit=self.slave_id
            )
            if not result.isError():
                data["power"] = result.registers[0]  # 0=Off, 1=Shutting down, 2=Starting, 3=Running
            
            # Read control state (Register 185)
            result = self._client.read_holding_registers(
                REGISTER_CONTROL_STATE, 1, unit=self.slave_id
            )
            if not result.isError():
                data["control_state"] = result.registers[0]  # 0=STOP, 1=AWAY, 2=HOME, 3=BOOST, etc.
            
            # Read speed control (Register 187)
            result = self._client.read_holding_registers(
                REGISTER_SPEED_CONTROL, 1, unit=self.slave_id
            )
            if not result.isError():
                data["speed_control"] = result.registers[0]  # 0=AUTO, 1=STOP, 2-6=SPEED1-5
            
            # Read temperature measurements (scaled by 10)
            result = self._client.read_holding_registers(
                REGISTER_FRESH_AIR_TEMP, 1, unit=self.slave_id
            )
            if not result.isError():
                data["fresh_air_temp"] = result.registers[0] / 10.0
            
            result = self._client.read_holding_registers(
                REGISTER_SUPPLY_TEMP, 1, unit=self.slave_id
            )
            if not result.isError():
                data["supply_temp"] = result.registers[0] / 10.0
            
            result = self._client.read_holding_registers(
                REGISTER_EXHAUST_TEMP, 1, unit=self.slave_id
            )
            if not result.isError():
                data["exhaust_temp"] = result.registers[0] / 10.0
            
            result = self._client.read_holding_registers(
                REGISTER_WASTE_TEMP, 1, unit=self.slave_id
            )
            if not result.isError():
                data["waste_temp"] = result.registers[0] / 10.0
            
            # Read temperature setpoints (scaled by 10)
            result = self._client.read_holding_registers(
                REGISTER_EXHAUST_TEMP_SETPOINT, 1, unit=self.slave_id
            )
            if not result.isError():
                data["exhaust_temp_setpoint"] = result.registers[0] / 10.0
            
            result = self._client.read_holding_registers(
                REGISTER_SUPPLY_TEMP_SETPOINT, 1, unit=self.slave_id
            )
            if not result.isError():
                data["supply_temp_setpoint"] = result.registers[0] / 10.0
            
            # Read fan speed settings
            result = self._client.read_holding_registers(
                REGISTER_HOME_SPEED, 1, unit=self.slave_id
            )
            if not result.isError():
                data["home_speed"] = result.registers[0]  # 0-4
            
            result = self._client.read_holding_registers(
                REGISTER_AWAY_SPEED, 1, unit=self.slave_id
            )
            if not result.isError():
                data["away_speed"] = result.registers[0]  # 0-4
            
            # Read state indicators
            result = self._client.read_holding_registers(
                REGISTER_HOME_STATE, 1, unit=self.slave_id
            )
            if not result.isError():
                data["home_state"] = result.registers[0]  # 0=Away, 1=Home
            
            result = self._client.read_holding_registers(
                REGISTER_BOOST_STATE, 1, unit=self.slave_id
            )
            if not result.isError():
                data["boost_state"] = result.registers[0]  # 0=Off, 1=On
            
            result = self._client.read_holding_registers(
                REGISTER_BOOST_TIMER, 1, unit=self.slave_id
            )
            if not result.isError():
                data["boost_timer"] = result.registers[0]  # minutes
            
            # Read additional sensors if available
            result = self._client.read_holding_registers(
                REGISTER_HUMIDITY, 1, unit=self.slave_id
            )
            if not result.isError():
                humidity = result.registers[0]
                if humidity >= 0:  # -1 means not available
                    data["humidity"] = humidity
            
            result = self._client.read_holding_registers(
                REGISTER_CO2, 1, unit=self.slave_id
            )
            if not result.isError():
                co2 = result.registers[0]
                if co2 >= 0:  # -1 means not available
                    data["co2"] = co2
            
            # Read alarm status
            result = self._client.read_holding_registers(
                REGISTER_ALARM_COUNT, 1, unit=self.slave_id
            )
            if not result.isError():
                data["alarm_count"] = result.registers[0]
            
            result = self._client.read_holding_registers(
                REGISTER_SUM_ALARM, 1, unit=self.slave_id
            )
            if not result.isError():
                data["sum_alarm"] = result.registers[0]  # 0=None, 1=Active
            
            _LOGGER.debug("Read data from Parmair: %s", data)
            return data
            
        except Exception as ex:
            _LOGGER.error("Error reading from Modbus: %s", ex)
            raise ModbusException(f"Failed to read data: {ex}") from ex

    def write_register(self, register: int, value: int) -> bool:
        """Write a value to a Modbus register."""
        try:
            if not self._client.connected:
                if not self._client.connect():
                    return False
            
            result = self._client.write_register(register, value, unit=self.slave_id)
            return not result.isError() if hasattr(result, 'isError') else result is not None
        except Exception as ex:
            _LOGGER.error("Error writing to Modbus register %s: %s", register, ex)
            return False

    async def async_write_register(self, register: int, value: int) -> bool:
        """Write a value to a Modbus register (async)."""
        return await self.hass.async_add_executor_job(self.write_register, register, value)

    async def async_shutdown(self) -> None:
        """Close the Modbus connection."""
        if self._client.connected:
            await self.hass.async_add_executor_job(self._client.close)
