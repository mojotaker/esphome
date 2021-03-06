import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import i2c
from esphome.const import CONF_ID, CONF_NUMBER, CONF_MODE, CONF_INVERTED

DEPENDENCIES = ['i2c']
MULTI_CONF = True

pcf8574_ns = cg.esphome_ns.namespace('pcf8574')
PCF8574GPIOMode = pcf8574_ns.enum('PCF8574GPIOMode')
PCF8674_GPIO_MODES = {
    'INPUT': PCF8574GPIOMode.PCF8574_INPUT,
    'INPUT_PULLUP': PCF8574GPIOMode.PCF8574_INPUT_PULLUP,
    'OUTPUT': PCF8574GPIOMode.PCF8574_OUTPUT,
}

PCF8574Component = pcf8574_ns.class_('PCF8574Component', cg.Component, i2c.I2CDevice)
PCF8574GPIOPin = pcf8574_ns.class_('PCF8574GPIOPin', cg.GPIOPin)

CONF_PCF8574 = 'pcf8574'
CONF_PCF8575 = 'pcf8575'
CONFIG_SCHEMA = cv.Schema({
    cv.Required(CONF_ID): cv.declare_variable_id(PCF8574Component),
    cv.Optional(CONF_PCF8575, default=False): cv.boolean,
}).extend(cv.COMPONENT_SCHEMA).extend(i2c.i2c_device_schema(0x21))


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(var, config)
    yield i2c.register_i2c_device(var, config)
    cg.add(var.set_pcf8575(config[CONF_PCF8575]))


PCF8574_OUTPUT_PIN_SCHEMA = cv.Schema({
    cv.Required(CONF_PCF8574): cv.use_variable_id(PCF8574Component),
    cv.Required(CONF_NUMBER): cv.int_,
    cv.Optional(CONF_MODE, default="OUTPUT"): cv.one_of(*PCF8674_GPIO_MODES, upper=True),
    cv.Optional(CONF_INVERTED, default=False): cv.boolean,
})
PCF8574_INPUT_PIN_SCHEMA = cv.Schema({
    cv.Required(CONF_PCF8574): cv.use_variable_id(PCF8574Component),
    cv.Required(CONF_NUMBER): cv.int_,
    cv.Optional(CONF_MODE, default="INPUT"): cv.one_of(*PCF8674_GPIO_MODES, upper=True),
    cv.Optional(CONF_INVERTED, default=False): cv.boolean,
})


@pins.PIN_SCHEMA_REGISTRY.register('pcf8574', (PCF8574_OUTPUT_PIN_SCHEMA, PCF8574_INPUT_PIN_SCHEMA))
def pcf8574_pin_to_code(config):
    parent = yield cg.get_variable(config[CONF_PCF8574])
    yield PCF8574GPIOPin.new(parent, config[CONF_NUMBER],
                             PCF8674_GPIO_MODES[config[CONF_MODE]], config[CONF_INVERTED])
