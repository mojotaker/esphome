from esphome import automation
from esphome.components import binary_sensor, cover
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_CLOSE_ACTION, CONF_CLOSE_DURATION, \
    CONF_CLOSE_ENDSTOP, CONF_ID, CONF_NAME, CONF_OPEN_ACTION, CONF_OPEN_DURATION, \
    CONF_OPEN_ENDSTOP, CONF_STOP_ACTION, CONF_MAX_DURATION

endstop_ns = cg.esphome_ns.namespace('endstop')
EndstopCover = endstop_ns.class_('EndstopCover', cover.Cover, cg.Component)

CONFIG_SCHEMA = cv.nameable(cover.COVER_SCHEMA.extend({
    cv.GenerateID(): cv.declare_variable_id(EndstopCover),
    cv.Required(CONF_STOP_ACTION): automation.validate_automation(single=True),

    cv.Required(CONF_OPEN_ENDSTOP): cv.use_variable_id(binary_sensor.BinarySensor),
    cv.Required(CONF_OPEN_ACTION): automation.validate_automation(single=True),
    cv.Required(CONF_OPEN_DURATION): cv.positive_time_period_milliseconds,

    cv.Required(CONF_CLOSE_ACTION): automation.validate_automation(single=True),
    cv.Required(CONF_CLOSE_ENDSTOP): cv.use_variable_id(binary_sensor.BinarySensor),
    cv.Required(CONF_CLOSE_DURATION): cv.positive_time_period_milliseconds,

    cv.Optional(CONF_MAX_DURATION): cv.positive_time_period_milliseconds,
}).extend(cv.COMPONENT_SCHEMA))


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_NAME])
    yield cg.register_component(var, config)
    yield cover.register_cover(var, config)

    yield automation.build_automation(var.get_stop_trigger(), [], config[CONF_STOP_ACTION])

    bin = yield cg.get_variable(config[CONF_OPEN_ENDSTOP])
    cg.add(var.set_open_endstop(bin))
    cg.add(var.set_open_duration(config[CONF_OPEN_DURATION]))
    yield automation.build_automation(var.get_open_trigger(), [], config[CONF_OPEN_ACTION])

    bin = yield cg.get_variable(config[CONF_CLOSE_ENDSTOP])
    cg.add(var.set_close_endstop(bin))
    cg.add(var.set_close_duration(config[CONF_CLOSE_DURATION]))
    yield automation.build_automation(var.get_close_trigger(), [], config[CONF_CLOSE_ACTION])

    if CONF_MAX_DURATION in config:
        cg.add(var.set_max_duration(config[CONF_MAX_DURATION]))
