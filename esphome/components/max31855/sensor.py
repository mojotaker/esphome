import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, spi
from esphome.const import CONF_ID, CONF_NAME, CONF_UPDATE_INTERVAL, \
    ICON_THERMOMETER, UNIT_CELSIUS

max31855_ns = cg.esphome_ns.namespace('max31855')
MAX31855Sensor = max31855_ns.class_('MAX31855Sensor', sensor.PollingSensorComponent, spi.SPIDevice)

CONFIG_SCHEMA = cv.nameable(
    sensor.sensor_schema(UNIT_CELSIUS, ICON_THERMOMETER, 1).extend({
        cv.GenerateID(): cv.declare_variable_id(MAX31855Sensor),
        cv.Optional(CONF_UPDATE_INTERVAL, default='60s'): cv.update_interval,
    }).extend(cv.COMPONENT_SCHEMA).extend(spi.SPI_DEVICE_SCHEMA))


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_NAME], config[CONF_UPDATE_INTERVAL])
    yield cg.register_component(var, config)
    yield spi.register_spi_device(var, config)
    yield sensor.register_sensor(var, config)
