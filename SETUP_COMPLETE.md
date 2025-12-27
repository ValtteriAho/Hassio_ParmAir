# Parmair Integration - Setup Complete

## ✅ What's Been Created

Your Parmair ventilation system integration for Home Assistant is now complete with proper Modbus register mappings from the v1.87 documentation.

### File Structure
```
custom_components/parmair/
├── manifest.json          # Integration metadata
├── __init__.py            # Main setup logic
├── config_flow.py         # UI configuration
├── coordinator.py         # Modbus data coordinator
├── const.py              # All register mappings
├── fan.py                # Fan entity (away/home/boost)
├── sensor.py             # Temperature & other sensors
└── strings.json          # UI translations
```

### Entities Provided

1. **Fan Entity** (`fan.parmair_ventilation`)
   - Control ventilation modes: Away, Home, Boost
   - Turn system on/off
   - Speed control via presets

2. **Temperature Sensors**
   - Fresh Air Temperature (outdoor)
   - Supply Air Temperature (into rooms)
   - Exhaust Air Temperature (from rooms)
   - Waste Air Temperature (exhausted outside)
   - Exhaust Temp Setpoint
   - Supply Temp Setpoint

3. **State Sensors**
   - Control State (mode)
   - Power State  
   - Home/Away State
   - Boost State
   - Boost Timer

4. **Optional Sensors** (if hardware present)
   - Humidity
   - CO2

5. **Alarm Sensors**
   - Alarm Count
   - Summary Alarm

## 📝 Key Register Mappings

| Function | Register | Address | Scaling |
|----------|----------|---------|---------|
| Power Control | 208 | 207 | 1 |
| Control State | 185 | 184 | 1 |
| Exhaust Temp | 24 | 23 | ÷10 |
| Supply Temp | 23 | 22 | ÷10 |
| Fresh Air Temp | 20 | 19 | ÷10 |
| Exhaust Setpoint | 60 | 59 | ÷10 |

**Note**: Register addresses are Register ID minus 1 (Modbus convention)

## 🚀 Next Steps

### 1. Install in Home Assistant

```bash
# Copy to Home Assistant
cp -r custom_components/parmair /config/custom_components/

# Or use the file editor in Home Assistant
```

### 2. Restart Home Assistant

### 3. Add the Integration
- Go to Settings → Devices & Services
- Click "+ ADD INTEGRATION"
- Search for "Parmair"
- Enter your device details:
  - **IP Address**: Your device's IP
  - **Port**: 502 (default)
  - **Slave ID**: 1 (default)
  - **Name**: "Parmair Ventilation" (or custom)

### 4. Test the Integration
- Check if all sensors appear
- Try switching between Away/Home/Boost modes
- Monitor temperature readings
- Check that timers and states update

## 🔧 Customization Options

### Adding More Registers
If you want to expose additional registers from the documentation, edit:
1. Add register address to `const.py`
2. Add reading logic to `coordinator.py`
3. Create appropriate entity in `sensor.py` or `fan.py`

### Adjusting Polling Interval
In `const.py`, change:
```python
DEFAULT_SCAN_INTERVAL = 30  # seconds
```

### Adding Binary Sensors
For alarm states, you could create `binary_sensor.py` to show alarms as on/off.

## 📚 Documentation

- **MODBUS_REGISTERS.md**: Complete register reference
- **Modbus Parmair v1.87.pdf**: Official Modbus specification
- **README.md**: User-facing documentation

## ⚠️ Important Notes

1. **Read-Only for Now**: Currently only reads data. Writing (control) is implemented in the fan entity for mode changes.

2. **Temperature Scaling**: All temperatures use factor 10 (value 210 = 21.0°C)

3. **Optional Sensors**: Humidity and CO2 only appear if available (register value >= 0)

4. **Power States**:
   - 0 = Off
   - 1 = Shutting down  
   - 2 = Starting
   - 3 = Running

5. **Control Modes**:
   - 0 = STOP
   - 1 = AWAY
   - 2 = HOME
   - 3 = BOOST
   - 4 = OVERPRESSURE
   - 5-8 = Timer variants
   - 9 = MANUAL

## 🐛 Troubleshooting

### Can't Connect
- Verify IP address and network connectivity
- Check firewall settings (port 502)
- Confirm Modbus is enabled on device

### Sensors Not Updating
- Check Home Assistant logs: Settings → System → Logs
- Look for "parmair" entries
- Verify register addresses match your device version

### Missing Sensors
- Optional sensors (humidity, CO2) require hardware
- Check coordinator data in developer tools

## 📞 Support

If you encounter issues:
1. Check Home Assistant logs
2. Enable debug logging:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.parmair: debug
   ```
3. Review MODBUS_REGISTERS.md for register details
4. Open GitHub issue with logs and configuration

---

**Integration is ready to use!** 🎉
