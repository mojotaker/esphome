import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_CURRENT, CONF_ID, CONF_POWER, CONF_UPDATE_INTERVAL, CONF_VOLTAGE, \
    UNIT_VOLT, ICON_FLASH, UNIT_AMPERE, UNIT_WATT

DEPENDENCIES = ['uart']

cse7766_ns = cg.esphome_ns.namespace('cse7766')
CSE7766Component = cse7766_ns.class_('CSE7766Component', cg.PollingComponent, uart.UARTDevice)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_variable_id(CSE7766Component),

    cv.Optional(CONF_VOLTAGE): cv.nameable(sensor.sensor_schema(UNIT_VOLT, ICON_FLASH, 1)),
    cv.Optional(CONF_CURRENT): cv.nameable(
        sensor.sensor_schema(UNIT_AMPERE, ICON_FLASH, 2)),
    cv.Optional(CONF_POWER): cv.nameable(sensor.sensor_schema(UNIT_WATT, ICON_FLASH, 1)),
    cv.Optional(CONF_UPDATE_INTERVAL, default='60s'): cv.update_interval,
}).extend(cv.COMPONENT_SCHEMA).extend(uart.UART_DEVICE_SCHEMA)


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_UPDATE_INTERVAL])
    yield cg.register_component(var, config)
    yield uart.register_uart_device(var, config)

    if CONF_VOLTAGE in config:
        conf = config[CONF_VOLTAGE]
        sens = yield sensor.new_sensor(conf)
        cg.add(var.set_voltage_sensor(sens))
    if CONF_CURRENT in config:
        conf = config[CONF_CURRENT]
        sens = yield sensor.new_sensor(conf)
        cg.add(var.set_current_sensor(sens))
    if CONF_POWER in config:
        conf = config[CONF_POWER]
        sens = yield sensor.new_sensor(conf)
        cg.add(var.set_power_sensor(sens))
