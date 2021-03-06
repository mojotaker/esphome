import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.automation import ACTION_REGISTRY, maybe_simple_id
from esphome.components.output import FloatOutput
from esphome.const import CONF_ID, CONF_IDLE_LEVEL, CONF_MAX_LEVEL, CONF_MIN_LEVEL, CONF_OUTPUT, \
    CONF_LEVEL

servo_ns = cg.esphome_ns.namespace('servo')
Servo = servo_ns.class_('Servo', cg.Component)
ServoWriteAction = servo_ns.class_('ServoWriteAction', cg.Action)
ServoDetachAction = servo_ns.class_('ServoDetachAction', cg.Action)

MULTI_CONF = True
CONFIG_SCHEMA = cv.Schema({
    cv.Required(CONF_ID): cv.declare_variable_id(Servo),
    cv.Required(CONF_OUTPUT): cv.use_variable_id(FloatOutput),
    cv.Optional(CONF_MIN_LEVEL, default='3%'): cv.percentage,
    cv.Optional(CONF_IDLE_LEVEL, default='7.5%'): cv.percentage,
    cv.Optional(CONF_MAX_LEVEL, default='12%'): cv.percentage,
}).extend(cv.COMPONENT_SCHEMA)


def to_code(config):
    out = yield cg.get_variable(config[CONF_OUTPUT])
    var = cg.new_Pvariable(config[CONF_ID], out)
    cg.register_component(var, config)

    cg.add(var.set_min_level(config[CONF_MIN_LEVEL]))
    cg.add(var.set_idle_level(config[CONF_IDLE_LEVEL]))
    cg.add(var.set_max_level(config[CONF_MAX_LEVEL]))


@ACTION_REGISTRY.register('servo.write', cv.Schema({
    cv.Required(CONF_ID): cv.use_variable_id(Servo),
    cv.Required(CONF_LEVEL): cv.templatable(cv.possibly_negative_percentage),
}))
def servo_write_to_code(config, action_id, template_arg, args):
    var = yield cg.get_variable(config[CONF_ID])
    type = ServoWriteAction.template(template_arg)
    rhs = type.new(var)
    action = cg.Pvariable(action_id, rhs, type=type)
    template_ = yield cg.templatable(config[CONF_LEVEL], args, float)
    cg.add(action.set_value(template_))
    yield action


@ACTION_REGISTRY.register('servo.detach', maybe_simple_id({
    cv.Required(CONF_ID): cv.use_variable_id(Servo),
}))
def servo_detach_to_code(config, action_id, template_arg, args):
    var = yield cg.get_variable(config[CONF_ID])
    type = ServoDetachAction.template(template_arg)
    rhs = type.new(var)
    yield cg.Pvariable(action_id, rhs, type=type)
