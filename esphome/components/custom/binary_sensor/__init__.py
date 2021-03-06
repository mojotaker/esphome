from esphome.components import binary_sensor
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_BINARY_SENSORS, CONF_ID, CONF_LAMBDA, CONF_NAME
from .. import custom_ns

CustomBinarySensorConstructor = custom_ns.class_('CustomBinarySensorConstructor')

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_variable_id(CustomBinarySensorConstructor),
    cv.Required(CONF_LAMBDA): cv.lambda_,
    cv.Required(CONF_BINARY_SENSORS):
        cv.ensure_list(cv.nameable(binary_sensor.BINARY_SENSOR_SCHEMA)),
})


def to_code(config):
    template_ = yield cg.process_lambda(
        config[CONF_LAMBDA], [], return_type=cg.std_vector.template(binary_sensor.BinarySensorPtr))

    rhs = CustomBinarySensorConstructor(template_)
    custom = cg.variable(config[CONF_ID], rhs)
    for i, conf in enumerate(config[CONF_BINARY_SENSORS]):
        rhs = custom.Pget_binary_sensor(i)
        cg.add(rhs.set_name(conf[CONF_NAME]))
        yield binary_sensor.register_binary_sensor(rhs, conf)
