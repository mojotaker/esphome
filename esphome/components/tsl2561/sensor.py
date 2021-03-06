import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c, sensor
from esphome.const import CONF_GAIN, CONF_ID, CONF_INTEGRATION_TIME, CONF_UPDATE_INTERVAL, CONF_NAME

DEPENDENCIES = ['i2c']

tsl2561_ns = cg.esphome_ns.namespace('tsl2561')
TSL2561IntegrationTime = tsl2561_ns.enum('TSL2561IntegrationTime')
INTEGRATION_TIMES = {
    14: TSL2561IntegrationTime.TSL2561_INTEGRATION_14MS,
    101: TSL2561IntegrationTime.TSL2561_INTEGRATION_101MS,
    402: TSL2561IntegrationTime.TSL2561_INTEGRATION_402MS,
}

TSL2561Gain = tsl2561_ns.enum('TSL2561Gain')
GAINS = {
    '1X': TSL2561Gain.TSL2561_GAIN_1X,
    '16X': TSL2561Gain.TSL2561_GAIN_16X,
}

CONF_IS_CS_PACKAGE = 'is_cs_package'


def validate_integration_time(value):
    value = cv.positive_time_period_milliseconds(value).total_milliseconds
    return cv.one_of(*INTEGRATION_TIMES, int=True)(value)


TSL2561Sensor = tsl2561_ns.class_('TSL2561Sensor', sensor.PollingSensorComponent, i2c.I2CDevice)

CONFIG_SCHEMA = cv.nameable(sensor.SENSOR_SCHEMA.extend({
    cv.GenerateID(): cv.declare_variable_id(TSL2561Sensor),
    cv.Optional(CONF_INTEGRATION_TIME, default=402): validate_integration_time,
    cv.Optional(CONF_GAIN, default='1X'): cv.one_of(*GAINS, upper=True),
    cv.Optional(CONF_IS_CS_PACKAGE, default=False): cv.boolean,
    cv.Optional(CONF_UPDATE_INTERVAL, default='60s'): cv.update_interval,
}).extend(cv.COMPONENT_SCHEMA).extend(i2c.i2c_device_schema(0x39)))


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_NAME], config[CONF_UPDATE_INTERVAL])
    yield cg.register_component(var, config)
    yield i2c.register_i2c_device(var, config)
    yield sensor.register_sensor(var, config)

    cg.add(var.set_integration_time(INTEGRATION_TIMES[config[CONF_INTEGRATION_TIME]]))
    cg.add(var.set_gain(GAINS[config[CONF_GAIN]]))
    cg.add(var.set_is_cs_package(config[CONF_IS_CS_PACKAGE]))
