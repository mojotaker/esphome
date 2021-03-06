# coding=utf-8
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c, sensor
from esphome.const import CONF_COLOR_TEMPERATURE, CONF_GAIN, CONF_ID, \
    CONF_ILLUMINANCE, CONF_INTEGRATION_TIME, CONF_UPDATE_INTERVAL, ICON_LIGHTBULB, \
    UNIT_PERCENT, ICON_THERMOMETER, UNIT_KELVIN, ICON_BRIGHTNESS_5, UNIT_LUX

DEPENDENCIES = ['i2c']

CONF_RED_CHANNEL = 'red_channel'
CONF_GREEN_CHANNEL = 'green_channel'
CONF_BLUE_CHANNEL = 'blue_channel'
CONF_CLEAR_CHANNEL = 'clear_channel'

tcs34725_ns = cg.esphome_ns.namespace('tcs34725')
TCS34725Component = tcs34725_ns.class_('TCS34725Component', cg.PollingComponent, i2c.I2CDevice)

TCS34725IntegrationTime = tcs34725_ns.enum('TCS34725IntegrationTime')
TCS34725_INTEGRATION_TIMES = {
    '2.4ms': TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_2_4MS,
    '24ms': TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_24MS,
    '50ms': TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_50MS,
    '101ms': TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_101MS,
    '154ms': TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_154MS,
    '700ms': TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_700MS,
}

TCS34725Gain = tcs34725_ns.enum('TCS34725Gain')
TCS34725_GAINS = {
    '1X': TCS34725Gain.TCS34725_GAIN_1X,
    '4X': TCS34725Gain.TCS34725_GAIN_4X,
    '16X': TCS34725Gain.TCS34725_GAIN_16X,
    '60X': TCS34725Gain.TCS34725_GAIN_60X,
}

color_channel_schema = sensor.sensor_schema(UNIT_PERCENT, ICON_LIGHTBULB, 1)
color_temperature_schema = sensor.sensor_schema(UNIT_KELVIN, ICON_THERMOMETER, 1)
illuminance_schema = sensor.sensor_schema(UNIT_LUX, ICON_BRIGHTNESS_5, 1)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_variable_id(TCS34725Component),
    cv.Optional(CONF_RED_CHANNEL): cv.nameable(color_channel_schema),
    cv.Optional(CONF_GREEN_CHANNEL): cv.nameable(color_channel_schema),
    cv.Optional(CONF_BLUE_CHANNEL): cv.nameable(color_channel_schema),
    cv.Optional(CONF_CLEAR_CHANNEL): cv.nameable(color_channel_schema),
    cv.Optional(CONF_ILLUMINANCE): cv.nameable(illuminance_schema),
    cv.Optional(CONF_COLOR_TEMPERATURE): cv.nameable(color_temperature_schema),
    cv.Optional(CONF_INTEGRATION_TIME, default='2.4ms'):
        cv.one_of(*TCS34725_INTEGRATION_TIMES, lower=True),
    cv.Optional(CONF_GAIN, default='1X'): cv.All(cv.Upper, cv.one_of(*TCS34725_GAINS), upper=True),
    cv.Optional(CONF_UPDATE_INTERVAL, default='60s'): cv.update_interval,
}).extend(cv.COMPONENT_SCHEMA).extend(i2c.i2c_device_schema(0x29))


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_UPDATE_INTERVAL])
    yield cg.register_component(var, config)
    yield i2c.register_i2c_device(var, config)

    cg.add(var.set_integration_time(TCS34725_INTEGRATION_TIMES[config[CONF_INTEGRATION_TIME]]))
    cg.add(var.set_gain(TCS34725_GAINS[config[CONF_GAIN]]))

    if CONF_RED_CHANNEL in config:
        sens = yield sensor.new_sensor(config[CONF_RED_CHANNEL])
        cg.add(var.set_red_sensor(sens))
    if CONF_GREEN_CHANNEL in config:
        sens = yield sensor.new_sensor(config[CONF_GREEN_CHANNEL])
        cg.add(var.set_green_sensor(sens))
    if CONF_BLUE_CHANNEL in config:
        sens = yield sensor.new_sensor(config[CONF_BLUE_CHANNEL])
        cg.add(var.set_blue_sensor(sens))
    if CONF_CLEAR_CHANNEL in config:
        sens = yield sensor.new_sensor(config[CONF_CLEAR_CHANNEL])
        cg.add(var.set_clear_sensor(sens))
    if CONF_ILLUMINANCE in config:
        sens = yield sensor.new_sensor(config[CONF_ILLUMINANCE])
        cg.add(var.set_illuminance_sensor(sens))
    if CONF_COLOR_TEMPERATURE in config:
        sens = yield sensor.new_sensor(config[CONF_COLOR_TEMPERATURE])
        cg.add(var.set_color_temperature_sensor(sens))
