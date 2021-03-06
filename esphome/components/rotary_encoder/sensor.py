import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import sensor
from esphome.const import CONF_ID, CONF_NAME, CONF_RESOLUTION, CONF_MIN_VALUE, CONF_MAX_VALUE

rotary_encoder_ns = cg.esphome_ns.namespace('rotary_encoder')
RotaryEncoderResolution = rotary_encoder_ns.enum('RotaryEncoderResolution')
RESOLUTIONS = {
    1: RotaryEncoderResolution.ROTARY_ENCODER_1_PULSE_PER_CYCLE,
    2: RotaryEncoderResolution.ROTARY_ENCODER_2_PULSES_PER_CYCLE,
    4: RotaryEncoderResolution.ROTARY_ENCODER_4_PULSES_PER_CYCLE,
}

CONF_PIN_A = 'pin_a'
CONF_PIN_B = 'pin_b'
CONF_PIN_RESET = 'pin_reset'

RotaryEncoderSensor = rotary_encoder_ns.class_('RotaryEncoderSensor', sensor.Sensor, cg.Component)


def validate_min_max_value(config):
    if CONF_MIN_VALUE in config and CONF_MAX_VALUE in config:
        min_val = config[CONF_MIN_VALUE]
        max_val = config[CONF_MAX_VALUE]
        if min_val >= max_val:
            raise cv.Invalid("Max value {} must be smaller than min value {}"
                             "".format(max_val, min_val))
    return config


CONFIG_SCHEMA = cv.nameable(sensor.SENSOR_SCHEMA.extend({
    cv.GenerateID(): cv.declare_variable_id(RotaryEncoderSensor),
    cv.Required(CONF_PIN_A): cv.All(pins.internal_gpio_input_pin_schema,
                                    pins.validate_has_interrupt),
    cv.Required(CONF_PIN_B): cv.All(pins.internal_gpio_input_pin_schema,
                                    pins.validate_has_interrupt),
    cv.Optional(CONF_PIN_RESET): pins.internal_gpio_input_pin_schema,
    cv.Optional(CONF_RESOLUTION, default=1): cv.one_of(*RESOLUTIONS, int=True),
    cv.Optional(CONF_MIN_VALUE): cv.int_,
    cv.Optional(CONF_MAX_VALUE): cv.int_,
}).extend(cv.COMPONENT_SCHEMA), validate_min_max_value)


def to_code(config):
    pin_a = yield cg.gpio_pin_expression(config[CONF_PIN_A])
    pin_b = yield cg.gpio_pin_expression(config[CONF_PIN_B])
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_NAME], pin_a, pin_b)
    yield cg.register_component(var, config)
    yield sensor.register_sensor(var, config)

    if CONF_PIN_RESET in config:
        pin_i = yield cg.gpio_pin_expression(config[CONF_PIN_RESET])
        cg.add(var.set_reset_pin(pin_i))
    if CONF_RESOLUTION in config:
        resolution = RESOLUTIONS[config[CONF_RESOLUTION]]
        cg.add(var.set_resolution(resolution))
    if CONF_MIN_VALUE in config:
        cg.add(var.set_min_value(config[CONF_MIN_VALUE]))
    if CONF_MAX_VALUE in config:
        cg.add(var.set_max_value(config[CONF_MAX_VALUE]))
