"""Constants for the Parmair integration."""

DOMAIN = "parmair"

# Configuration
CONF_SLAVE_ID = "slave_id"
DEFAULT_NAME = "Parmair Ventilation"
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1

# Modbus register addresses (subtract 1 from register ID in documentation)
# Power and Control
REGISTER_POWER = 207  # Register 208: POWER_BTN_FI
REGISTER_CONTROL_STATE = 184  # Register 185: IV01_CONTROLSTATE_FO
REGISTER_SPEED_CONTROL = 186  # Register 187: IV01_SPEED_FOC

# Temperature measurements (read only, scaled by 10)
REGISTER_FRESH_AIR_TEMP = 19  # Register 20: TE01_M
REGISTER_SUPPLY_TEMP = 22  # Register 23: TE10_M
REGISTER_EXHAUST_TEMP = 23  # Register 24: TE30_M
REGISTER_WASTE_TEMP = 24  # Register 25: TE31_M

# Temperature setpoints (read/write, scaled by 10)
REGISTER_EXHAUST_TEMP_SETPOINT = 59  # Register 60: TE30_S
REGISTER_SUPPLY_TEMP_SETPOINT = 64  # Register 65: TE10_S

# Fan speed settings (read/write)
REGISTER_HOME_SPEED = 103  # Register 104: HOME_SPEED_S
REGISTER_AWAY_SPEED = 104  # Register 105: AWAY_SPEED_S
REGISTER_BOOST_SETTING = 116  # Register 117: BOOST_SETTING_S

# State indicators (read only)
REGISTER_HOME_STATE = 199  # Register 200: HOME_STATE_FI
REGISTER_BOOST_STATE = 200  # Register 201: BOOST_STATE_FI
REGISTER_BOOST_TIMER = 201  # Register 202: BOOST_TIMER_FM

# Additional sensors
REGISTER_HUMIDITY = 179  # Register 180: MEXX_FM
REGISTER_CO2 = 30  # Register 31: QE20_M

# Alarms
REGISTER_ALARM_COUNT = 3  # Register 4: ALARM_COUNT
REGISTER_SUM_ALARM = 4  # Register 5: SUM_ALARM
REGISTER_ALARMS_STATE = 205  # Register 206: ALARMS_STATE_FI

# Operating modes for IV01_CONTROLSTATE_FO (Register 185)
MODE_STOP = 0
MODE_AWAY = 1
MODE_HOME = 2
MODE_BOOST = 3
MODE_OVERPRESSURE = 4
MODE_AWAY_TIMER = 5
MODE_HOME_TIMER = 6
MODE_BOOST_TIMER = 7
MODE_OVERPRESSURE_TIMER = 8
MODE_MANUAL = 9

# Speed control values for IV01_SPEED_FOC (Register 187)
SPEED_AUTO = 0
SPEED_STOP = 1
SPEED_1 = 2
SPEED_2 = 3
SPEED_3 = 4
SPEED_4 = 5
SPEED_5 = 6

# Power button states (Register 208)
POWER_OFF = 0
POWER_SHUTTING_DOWN = 1
POWER_STARTING = 2
POWER_RUNNING = 3
