# Contributing to Parmair MAC Integration

Thank you for your interest in contributing to the Parmair MAC Home Assistant integration!

## Development Setup

### Prerequisites
- Home Assistant development environment
- Python 3.11 or newer
- Access to a Parmair MAC device for testing

### Installation for Development

1. Clone the repository:
   ```bash
   git clone https://github.com/ValtteriAho/Hassio_Parmair.git
   cd Hassio_Parmair
   ```

2. Copy to your Home Assistant custom_components directory:
   ```bash
   cp -r custom_components/parmair /path/to/homeassistant/custom_components/
   ```

3. Restart Home Assistant

## Architecture

This integration follows Home Assistant's development guidelines and uses:

- **pymodbus>=3.11.2** for Modbus TCP communication
- **Modern pymodbus 3.x API** (legacy compatibility code removed in v0.10.0)
- **DataUpdateCoordinator** for efficient data fetching with configurable timing
- **Config flow** with auto-detection and manual fallback
- **Proper error handling** and connection management

### Key Components

#### `coordinator.py`
- Manages Modbus TCP connection and data polling
- Handles register reads/writes with proper scaling
- Implements connection buffering and timing optimizations
- Reconnects on every poll cycle to prevent transaction ID conflicts

#### `const.py`
- Register definitions for v1.xx and v2.xx software versions
- Register metadata (address, label, scale, read/write permissions)
- Version-specific register mappings

#### `config_flow.py`
- UI configuration flow
- Auto-detection of software version and heater type
- Manual fallback if auto-detection fails
- Connection validation

#### Platform Files
- `fan.py` - Main ventilation control entity
- `sensor.py` - Temperature, state, and diagnostic sensors
- `switch.py` - Mode switches (summer, time program, heater, boost, overpressure)
- `button.py` - Action buttons (acknowledge alarms, filter replaced)
- `number.py` - Numeric settings (speeds, setpoints, timers)
- `select.py` - Dropdown selections (heater type)

## Modbus Communication

### Register Addressing
- Modbus Address = Register ID + 1000
- Example: Register ID 15 → Modbus Address 1015

### Timing Optimizations
The integration includes several timing optimizations to prevent Modbus transaction conflicts:

- **0.3 second delay** after connecting
- **0.2 second delay** between register reads
- **0.2 second delay** after writes
- **Connection cycling**: Close and reconnect on every poll to flush buffers

### Software Version Differences

#### Software 1.x (Modbus spec 1.87)
- Older MAC models (pre-2023)
- Heater type register: 0=Water, 1=Electric, 2=None
- Limited sensor support

#### Software 2.x (Modbus spec 2.28)
- Newer MAC 2 and updated controllers
- Heater type register: 0=Electric, 1=Water, 2=None (reversed!)
- Additional sensors (exhaust CO2, extended diagnostics)

## Testing

### Manual Testing
1. Test with both v1.xx and v2.xx devices if possible
2. Verify auto-detection works correctly
3. Test all entity types (fan, sensors, switches, buttons, numbers, selects)
4. Verify writable registers (speeds, setpoints, modes)
5. Check error handling (disconnect device, invalid values)

### Common Test Scenarios
- Initial setup with auto-detection
- Initial setup with manual selection
- Connection loss and recovery
- Invalid register values (negative temperatures during calibration)
- Rapid state changes (boost mode on/off)

## Code Style

- Follow Home Assistant's code style guidelines
- Use type hints for all functions
- Include docstrings for classes and public methods
- Use descriptive variable names
- Keep functions focused and single-purpose

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test thoroughly with real hardware
5. Commit with clear, descriptive messages
6. Push to your fork
7. Open a Pull Request with:
   - Description of changes
   - Testing performed
   - Hardware/software versions tested

## Technical Reference

### Register Documentation
- `MODBUS_REGISTERS_1XX.md` - Complete v1.xx register map
- `MODBUS_REGISTERS_2XX.md` - Complete v2.xx register map

### Data Types
- int16 registers (signed 16-bit integers)
- Temperature scaling: value × 0.1 (210 = 21.0°C)
- Software version scaling: value × 0.01 (234 = 2.34)

### Optional Sensors
Some sensors have `optional=True` flag:
- If device returns -1, coordinator returns `None`
- Entity becomes "unavailable" in Home Assistant
- Used for hardware that may not be installed (humidity sensors)

**Exception**: CO2 exhaust sensor (v2.xx) should NOT be optional as it's standard on MAC 2 devices.

## Common Issues

### Transaction ID Mismatches
- Caused by requests sent faster than device can respond
- Integration includes timing delays to mitigate this
- Reconnecting on every poll cycle helps flush stale responses

### Heater Type Detection
- Values are reversed between v1.xx and v2.xx!
- Always check software version before interpreting heater type
- See constants in `const.py` for correct mappings

### CO2 Sensor Updates Stopping
- CO2 sensors may return -1 during calibration
- If marked as optional, updates stop until HA restart
- Solution: Don't mark standard sensors as optional

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Questions?

Feel free to open an issue on GitHub if you have questions or need clarification on any aspect of the integration.
