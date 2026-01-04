"""Config flow for Parmair integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pymodbus.client import ModbusTcpClient

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_integration


def _set_legacy_unit(client: ModbusTcpClient, unit_id: int) -> None:
    """Best-effort assignment for clients requiring attribute-based unit selection."""

    for attr in ("unit_id", "slave_id", "unit", "slave"):
        if hasattr(client, attr):
            try:
                setattr(client, attr, unit_id)
            except Exception:  # pragma: no cover
                continue


from .const import (
    CONF_FIRMWARE_VERSION,
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DEFAULT_FIRMWARE,
    DEFAULT_MODEL,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    FIRMWARE_V1,
    FIRMWARE_V2,
    MODEL_UNKNOWN,
    REG_HARDWARE_TYPE,
    REG_POWER,
    REG_SOFTWARE_VERSION,
    SUPPORTED_MODELS,
    detect_firmware_version,
    get_register_definition,
)

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=247)
        ),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=5, max=300)
        ),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


async def validate_connection(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    client = ModbusTcpClient(host=data[CONF_HOST], port=data[CONF_PORT])
    
    def _connect():
        """Connect to the Modbus device."""
        return client.connect()
    
    # Run the blocking connection in executor
    connected = await hass.async_add_executor_job(_connect)
    
    if not connected:
        client.close()
        raise CannotConnect
    
    # Auto-detect hardware model by reading VENT_MACHINE register
    def _detect_model_and_firmware():
        """Detect hardware model and firmware version from device."""
        detected_model = DEFAULT_MODEL
        detected_firmware = DEFAULT_FIRMWARE
        
        try:
            # Read hardware type register
            hardware_reg = get_register_definition(DEFAULT_MODEL, REG_HARDWARE_TYPE, DEFAULT_FIRMWARE)
            try:
                result = client.read_holding_registers(
                    hardware_reg.address, 1, unit=data[CONF_SLAVE_ID]
                )
            except TypeError:
                try:
                    result = client.read_holding_registers(
                        hardware_reg.address, 1, slave=data[CONF_SLAVE_ID]
                    )
                except TypeError:
                    try:
                        result = client.read_holding_registers(
                            hardware_reg.address, 1, device_id=data[CONF_SLAVE_ID]
                        )
                    except TypeError:
                        _set_legacy_unit(client, data[CONF_SLAVE_ID])
                        try:
                            result = client.read_holding_registers(
                                hardware_reg.address, 1
                            )
                        except TypeError:
                            result = client.read_holding_registers(
                                hardware_reg.address
                            )
            
            # Extract hardware type value
            if hasattr(result, "registers"):
                hardware_type = result.registers[0]
            elif isinstance(result, (list, tuple)):
                hardware_type = result[0]
            else:
                hardware_type = result
            
            # Format model based on VENT_MACHINE value
            if hardware_type in (80, 100, 150):
                detected_model = f"MAC{hardware_type}"
            else:
                detected_model = MODEL_UNKNOWN
            
            _LOGGER.info(
                "Auto-detected VENT_MACHINE value: %s, model: %s",
                hardware_type,
                detected_model,
            )
        except Exception as ex:
            _LOGGER.warning("Could not auto-detect model, using default: %s", ex)
        
        # Try to read software version to determine firmware family
        try:
            sw_reg = get_register_definition(DEFAULT_MODEL, REG_SOFTWARE_VERSION, DEFAULT_FIRMWARE)
            try:
                result = client.read_holding_registers(
                    sw_reg.address, 1, unit=data[CONF_SLAVE_ID]
                )
            except TypeError:
                try:
                    result = client.read_holding_registers(
                        sw_reg.address, 1, slave=data[CONF_SLAVE_ID]
                    )
                except TypeError:
                    _set_legacy_unit(client, data[CONF_SLAVE_ID])
                    result = client.read_holding_registers(
                        sw_reg.address, 1
                    )
            
            # Extract and scale software version
            if hasattr(result, "registers"):
                raw_sw = result.registers[0]
            elif isinstance(result, (list, tuple)):
                raw_sw = result[0]
            else:
                raw_sw = result
            
            sw_version = raw_sw * sw_reg.scale
            detected_firmware = detect_firmware_version(sw_version)
            
            _LOGGER.info(
                "Auto-detected MULTI_SW_VER: %s, firmware: %s",
                sw_version,
                detected_firmware,
            )
        except Exception as ex:
            _LOGGER.warning("Could not auto-detect firmware version, using default: %s", ex)
        
        return detected_model, detected_firmware
    
    detected_model, detected_firmware = await hass.async_add_executor_job(_detect_model_and_firmware)
    
    # Verify communication by reading a register with detected model
    power_register = get_register_definition(detected_model, REG_POWER, detected_firmware)
    
    # Try to read a register to verify communication
    def _read_test():
        """Test reading from the device."""
        try:
            result = client.read_holding_registers(
                power_register.address, 1, unit=data[CONF_SLAVE_ID]
            )
        except TypeError:
            try:
                # Older pymodbus versions expect the keyword 'slave'
                result = client.read_holding_registers(
                    power_register.address, 1, slave=data[CONF_SLAVE_ID]
                )
            except TypeError:
                try:
                    # Even older pymodbus versions expect 'device_id' keyword
                    result = client.read_holding_registers(
                        power_register.address, 1, device_id=data[CONF_SLAVE_ID]
                    )
                except TypeError:
                    # Very old clients require positional arguments only or attribute assignment
                    _set_legacy_unit(client, data[CONF_SLAVE_ID])
                    try:
                        result = client.read_holding_registers(
                            power_register.address, 1
                        )
                    except TypeError:
                        result = client.read_holding_registers(
                            power_register.address
                        )
        return not result.isError() if hasattr(result, 'isError') else result is not None
    
    try:
        success = await hass.async_add_executor_job(_read_test)
        if not success:
            raise CannotConnect
    finally:
        client.close()
    
    return {"title": data[CONF_NAME], "model": detected_model, "firmware_version": detected_firmware}


class ParmairConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Parmair."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""

        self._integration_version: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if self._integration_version is None:
            try:
                integration = await async_get_integration(self.hass, DOMAIN)
                self._integration_version = integration.version or "unknown"
            except Exception:  # pragma: no cover - fallback if manifest missing
                self._integration_version = "unknown"

        if user_input is not None:
            # Create unique ID based on host and slave ID
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}_{user_input[CONF_SLAVE_ID]}"
            )
            self._abort_if_unique_id_configured()
            
            try:
                info = await validate_connection(self.hass, user_input)
                # Add auto-detected model and firmware version to the data
                user_input[CONF_MODEL] = info["model"]
                user_input[CONF_FIRMWARE_VERSION] = info["firmware_version"]
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "version": self._integration_version or "unknown",
                "model": info.get("model", "MAC") if user_input and not errors else "MAC",
                "firmware": info.get("firmware_version", FIRMWARE_V1) if user_input and not errors else FIRMWARE_V1,
            },
        )
