# Parmair MAC - Home Assistant Integration v0.10.7

![Parmair MAC Logo](parmair_logo.jpg)

A custom Home Assistant integration for Parmair MAC ventilation systems via Modbus TCP communication.

## Features

- **Fan Control**: Control your Parmair ventilation unit including:
  - Power on/off
  - Mode selection (Away, Home, Boost)
  - Speed control via presets

- **Number Controls**: Adjust ventilation settings:
  - Home Speed Preset (0-4)
  - Away Speed Preset (0-4)
  - Boost Setting (2-4)
  - Exhaust Temperature Setpoint (18-26°C)
  - Supply Temperature Setpoint (15-25°C)

- **Switch Controls**: Toggle system features:
  - Summer Mode Enable/Disable
  - Time Program Enable/Disable
  - Heater Enable/Disable
  
- **Temperature Monitoring**: Real-time monitoring of:
  - Fresh air temperature
  - Supply air temperature  
  - Exhaust air temperature
  - Waste air temperature
  - Temperature setpoints
  
- **Additional Sensors** (if available):
  - Humidity
  - CO2 levels
  - Alarm status
  - Boost timer
  - Software version (Multi24 controller)
  - Diagnostic information in entity attributes
  
- **Local Polling**: Direct communication with your device via Modbus TCP
- **Automatic Model Detection**: Reads hardware type to identify MAC80/MAC100/MAC150 automatically
- **Software Version Detection**: Automatically detects software version (1.x or 2.x) for optimal register mapping

## System Information

This integration supports Parmair "My Air Control" systems:
- **Software 1.x**: Fully supported (Modbus spec 1.87)
- **Software 2.x**: Fully supported (Modbus spec 2.28)

## Installation

### HACS Installation (Recommended)

1. Open HACS in Home Assistant
2. Click the 3 dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL: `https://github.com/ValtteriAho/Hassio_Parmair`
5. Select category: "Integration"
6. Click "Add"
7. Find "Parmair MAC" in HACS and click "Download"
8. Restart Home Assistant
9. Go to Settings → Devices & Services → Add Integration
10. Search for "Parmair MAC"
11. Enter your device's connection details:
    - IP Address
    - Port (default: 502)
    - Modbus Slave ID (default: 0)
    - Polling Interval (default: 30 seconds)
    - Name (optional)

Hardware model and software version will be auto-detected from the device. If auto-detection fails, you can manually select software version and heater type.

## Configuration

The integration is configured through the Home Assistant UI. You'll need:

- **IP Address**: The IP address of your Parmair device
- **Port**: The Modbus TCP port (typically 502)
- **Slave ID**: The Modbus slave ID of your device (typically 0)

The hardware model (MAC80/MAC100/MAC150) and software version (1.x/2.x) are automatically detected. If detection fails during setup, you can manually select your software version and heater type.

## Entities Created

### Fan Entity
- **parmair_mac**: Main control for the ventilation system
  - Presets: Away, Home, Boost
  - Speed control (percentage based on preset)

### Number Entities
- **Home Speed Preset**: Adjust fan speed for Home mode (0-4)
- **Away Speed Preset**: Adjust fan speed for Away mode (0-4)
- **Boost Setting**: Set boost fan speed level (2-4)
- **Exhaust Temperature Setpoint**: Target exhaust air temperature (18-26°C)
- **Supply Temperature Setpoint**: Target supply air temperature (15-25°C)

### Switch Entities
- **Summer Mode**: Enable/disable summer mode operation
- **Time Program Enable**: Enable/disable scheduled time programs
- **Heater Enable**: Enable/disable heating element

> **⚠️ Heater Control Warning:**
> 
> Disabling the heating elements entirely carries inherent risks and may void warranty coverage. While heating elements are the primary energy-consuming components in the ventilation system, they are essential for freeze protection and optimal operation.
> 
> When using external automation systems (such as Home Assistant) to override the device's built-in control logic, the manufacturer cannot accept liability for component failures or malfunctions that occur during the warranty period. Any damage resulting from modified heater control settings may not be covered under warranty.

### Sensor Entities
- **Fresh Air Temperature**: Outdoor air temperature
- **Supply Air Temperature**: Air temperature being supplied to rooms
- **Exhaust Air Temperature**: Air temperature being extracted
- **Waste Air Temperature**: Air temperature being exhausted outside
- **Exhaust/Supply Temperature Setpoints**: Target temperatures
- **Control State**: Current operating mode (Stop, Away, Home, Boost, etc.)
- **Power State**: Power status (Off, Shutting Down, Starting, Running)
- **Home/Away State**: Whether system is in home or away mode (Home/Away)
- **Boost State**: Whether boost mode is active (On/Off)
- **Boost Timer**: Remaining boost time in minutes
- **Alarm Count**: Number of active alarms
- **Summary Alarm**: Overall alarm status

Optional sensors (if hardware is present):
- **Humidity**: Indoor humidity level
- **CO2 Exhaust Air**: Exhaust air CO2 concentration (software 2.x only, MAC 2 devices)
- Entity attributes include diagnostic information to aid troubleshooting

Diagnostic sensors:
- **Software Version**: Multi24 controller software version (used for version family detection)
- **Software Family**: Automatically detected as 1.x or 2.x based on software version

## Troubleshooting

For developer documentation, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Troubleshooting

### Connection Issues
- Verify the IP address is correct and the device is on the same network
- Check that Modbus TCP port is accessible (default port 502)
- Confirm the Modbus slave ID matches your device configuration (typically 0 for Parmair devices)
- If experiencing "transaction_id mismatch" errors, the integration includes timing optimizations
- Default slave ID changed from 1 to 0 in v0.9.0.5 to match Parmair device responses

### Missing Sensors
- Some sensors (humidity, CO2) only appear if the hardware is installed
- Check the device's Modbus configuration to ensure sensors are enabled

## Support

For issues, feature requests, or questions, please open an issue on GitHub.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## License

MIT License

---

## Disclaimer

This is an independent, personal project developed by a community member and is **not affiliated with, endorsed by, or supported by Parmair or its parent companies**. This integration is provided as-is, without any warranty or guarantee. The Parmair name and product references are used solely for identification purposes.

For official support, product information, or warranty claims, please contact Parmair directly through their official channels.

Use of this integration is at your own risk. The author assumes no liability for any damage, malfunction, or warranty voidance that may result from using this software with your Parmair ventilation system.
