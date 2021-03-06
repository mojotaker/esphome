from esphome import pins
from esphome.components import sensor
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_CLK_PIN, CONF_GAIN, CONF_ID, CONF_NAME, CONF_UPDATE_INTERVAL, \
    ICON_SCALE

hx711_ns = cg.esphome_ns.namespace('hx711')
HX711Sensor = hx711_ns.class_('HX711Sensor', sensor.PollingSensorComponent)

CONF_DOUT_PIN = 'dout_pin'

HX711Gain = hx711_ns.enum('HX711Gain')
GAINS = {
    128: HX711Gain.HX711_GAIN_128,
    32: HX711Gain.HX711_GAIN_32,
    64: HX711Gain.HX711_GAIN_64,
}

CONFIG_SCHEMA = cv.nameable(sensor.sensor_schema('', ICON_SCALE, 0).extend({
    cv.GenerateID(): cv.declare_variable_id(HX711Sensor),
    cv.Required(CONF_DOUT_PIN): pins.gpio_input_pin_schema,
    cv.Required(CONF_CLK_PIN): pins.gpio_output_pin_schema,
    cv.Optional(CONF_GAIN, default=128): cv.one_of(*GAINS, int=True),
    cv.Optional(CONF_UPDATE_INTERVAL, default='60s'): cv.update_interval,
}).extend(cv.COMPONENT_SCHEMA))


def to_code(config):
    dout_pin = yield cg.gpio_pin_expression(config[CONF_DOUT_PIN])
    sck_pin = yield cg.gpio_pin_expression(config[CONF_CLK_PIN])
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_NAME], dout_pin, sck_pin,
                           config[CONF_UPDATE_INTERVAL])
    yield cg.register_component(var, config)
    yield sensor.register_sensor(var, config)

    cg.add(var.set_gain(GAINS[config[CONF_GAIN]]))
