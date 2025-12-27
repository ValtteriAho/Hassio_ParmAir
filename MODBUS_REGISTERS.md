# Parmair Modbus Register Documentation

Based on "Modbus Parmair v1.87" documentation

## Important Notes
- **Register addressing**: Modbus register IDs in documentation start at 1. In Modbus protocol, subtract 1 for actual address (Register 1 = Address 0)
- **Data type**: All registers are int16 (Holding Registers, Function Codes 03, 06, 16)
- **Temperature scaling**: Temperatures use factor 10 (value 210 = 21.0°C)
- **Percentage values**: Some use factor 1, some use factor 10

## Key Registers for Home Assistant Integration

### Power & Control State
| Register | Address | Name | Description | Scaling | Values |
|----------|---------|------|-------------|---------|--------|
| 208 | 207 | POWER_BTN_FI | Power button state | 1 | 0=Off, 1=Shutting down, 2=Starting, 3=Running |
| 185 | 184 | IV01_CONTROLSTATE_FO | Control state | 1 | 0=STOP, 1=AWAY, 2=HOME, 3=BOOST, 4=OVERPRESSURE, 5-8=Time program variants, 9=MANUAL |
| 187 | 186 | IV01_SPEED_FOC | Speed control | 1 | 0=AUTO, 1=STOP, 2=SPEED1, 3=SPEED2, 4=SPEED3, 5=SPEED4, 6=SPEED5 |

### Temperature Measurements (Read Only)
| Register | Address | Name | Description | Scaling | Unit |
|----------|---------|------|-------------|---------|------|
| 20 | 19 | TE01_M | Fresh air temperature | 10 | °C |
| 23 | 22 | TE10_M | Supply air temperature | 10 | °C |
| 24 | 23 | TE30_M | Exhaust air temperature | 10 | °C |
| 25 | 24 | TE31_M | Waste air temperature | 10 | °C |

### Temperature Setpoints (Read/Write)
| Register | Address | Name | Description | Scaling | Range | Unit |
|----------|---------|------|-------------|---------|-------|------|
| 60 | 59 | TE30_S | Exhaust air temp setpoint | 10 | 18.0-26.0 | °C |
| 65 | 64 | TE10_S | Supply air temp setpoint | 10 | 15.0-25.0 | °C |

### Fan Speed Settings (Read/Write)
| Register | Address | Name | Description | Scaling | Range | Unit |
|----------|---------|------|-------------|---------|-------|------|
| 104 | 103 | HOME_SPEED_S | Speed when home | 1 | 0-4 | level |
| 105 | 104 | AWAY_SPEED_S | Speed when away | 1 | 0-4 | level |
| 117 | 116 | BOOST_SETTING_S | Boost speed setting | 1 | 2-4 (=speeds 3-5) | level |
| 120 | 119 | FAN_SPEED1_S | Fan speed 1 percentage | 1 | 10-100 | % |
| 121 | 120 | FAN_SPEED2_S | Fan speed 2 percentage | 1 | 10-100 | % |
| 122 | 121 | FAN_SPEED3_S | Fan speed 3 percentage | 1 | 10-100 | % |
| 123 | 122 | FAN_SPEED4_S | Fan speed 4 percentage | 1 | 10-100 | % |
| 124 | 123 | FAN_SPEED5_S | Fan speed 5 percentage | 1 | 10-100 | % |

### Timers & States (Read/Write for timers, Read Only for most states)
| Register | Address | Name | Description | Scaling | Unit |
|----------|---------|------|-------------|---------|------|
| 200 | 199 | HOME_STATE_FI | Home state | 1 | 0=Away, 1=Home |
| 201 | 200 | BOOST_STATE_FI | Boost active | 1 | 0=Off, 1=On |
| 202 | 201 | BOOST_TIMER_FM | Boost timer | 1 | minutes |
| 203 | 202 | OVERP_STATE_FI | Overpressure active | 1 | 0=Off, 1=On |
| 204 | 203 | OVERP_TIMER_FM | Overpressure timer | 1 | minutes |

### Additional Sensors
| Register | Address | Name | Description | Scaling | Unit |
|----------|---------|------|-------------|---------|------|
| 30 | 29 | ME20_M | Humidity, humid space | 1 | %Rh |
| 31 | 30 | QE20_M | CO2 measurement | 1 | ppm |
| 180 | 179 | MEXX_FM | Humidity, main display | 1 | %Rh |

### Alarms
| Register | Address | Name | Description |
|----------|---------|------|-------------|
| 3 | 2 | ACK_ALARMS | Acknowledge alarms (0=Waiting, 1=OK/ACK) |
| 4 | 3 | ALARM_COUNT | Active alarm count |
| 5 | 4 | SUM_ALARM | Summary alarm (0=None, 1=Active) |
| 206 | 205 | ALARMS_STATE_FI | Alarm state (0=OK, 1=Alarms active, 2=Filter dirty) |

### Configuration
| Register | Address | Name | Description | Values |
|----------|---------|------|-------------|--------|
| 108 | 107 | TP_ENABLE_S | Time program enable | 0=Disabled, 1=Enabled |
| 244 | 243 | VENT_MACHINE | Machine type number | e.g., 80=MAC 80, 105=MAC 105 |
