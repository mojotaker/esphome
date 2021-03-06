import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.automation import ACTION_REGISTRY
from esphome.components import mqtt
from esphome.const import CONF_AWAY, CONF_ID, CONF_INTERNAL, CONF_MAX_TEMPERATURE, \
    CONF_MIN_TEMPERATURE, CONF_MODE, CONF_TARGET_TEMPERATURE, \
    CONF_TARGET_TEMPERATURE_HIGH, CONF_TARGET_TEMPERATURE_LOW, CONF_TEMPERATURE_STEP, CONF_VISUAL, \
    CONF_MQTT_ID
from esphome.core import CORE, coroutine

climate_ns = cg.esphome_ns.namespace('climate')

ClimateDevice = climate_ns.class_('Climate', cg.Nameable)
ClimateCall = climate_ns.class_('ClimateCall')
ClimateTraits = climate_ns.class_('ClimateTraits')
# MQTTClimateComponent = climate_ns.class_('MQTTClimateComponent', mqtt.MQTTComponent)

ClimateMode = climate_ns.enum('ClimateMode')
CLIMATE_MODES = {
    'OFF': ClimateMode.CLIMATE_MODE_OFF,
    'AUTO': ClimateMode.CLIMATE_MODE_AUTO,
    'COOL': ClimateMode.CLIMATE_MODE_COOL,
    'HEAT': ClimateMode.CLIMATE_MODE_HEAT,
}

validate_climate_mode = cv.one_of(*CLIMATE_MODES, upper=True)

# Actions
ControlAction = climate_ns.class_('ControlAction', cg.Action)

CLIMATE_SCHEMA = cv.MQTT_COMMAND_COMPONENT_SCHEMA.extend({
    cv.GenerateID(): cv.declare_variable_id(ClimateDevice),
    cv.OnlyWith(CONF_MQTT_ID, 'mqtt'): cv.declare_variable_id(mqtt.MQTTClimateComponent),
    cv.Optional(CONF_VISUAL, default={}): cv.Schema({
        cv.Optional(CONF_MIN_TEMPERATURE): cv.temperature,
        cv.Optional(CONF_MAX_TEMPERATURE): cv.temperature,
        cv.Optional(CONF_TEMPERATURE_STEP): cv.temperature,
    }),
    # TODO: MQTT topic options
})


@coroutine
def setup_climate_core_(var, config):
    if CONF_INTERNAL in config:
        cg.add(var.set_internal(config[CONF_INTERNAL]))
    visual = config[CONF_VISUAL]
    if CONF_MIN_TEMPERATURE in visual:
        cg.add(var.set_visual_min_temperature_override(visual[CONF_MIN_TEMPERATURE]))
    if CONF_MAX_TEMPERATURE in visual:
        cg.add(var.set_visual_max_temperature_override(visual[CONF_MAX_TEMPERATURE]))
    if CONF_TEMPERATURE_STEP in visual:
        cg.add(var.set_visual_temperature_step_override(visual[CONF_TEMPERATURE_STEP]))

    if CONF_MQTT_ID in config:
        mqtt_ = cg.new_Pvariable(config[CONF_MQTT_ID], var)
        yield mqtt.register_mqtt_component(mqtt_, config)


@coroutine
def register_climate(var, config):
    if not CORE.has_id(config[CONF_ID]):
        var = cg.Pvariable(config[CONF_ID], var)
    cg.add(cg.App.register_climate(var))
    yield setup_climate_core_(var, config)


CLIMATE_CONTROL_ACTION_SCHEMA = cv.Schema({
    cv.Required(CONF_ID): cv.use_variable_id(ClimateDevice),
    cv.Optional(CONF_MODE): cv.templatable(validate_climate_mode),
    cv.Optional(CONF_TARGET_TEMPERATURE): cv.templatable(cv.temperature),
    cv.Optional(CONF_TARGET_TEMPERATURE_LOW): cv.templatable(cv.temperature),
    cv.Optional(CONF_TARGET_TEMPERATURE_HIGH): cv.templatable(cv.temperature),
    cv.Optional(CONF_AWAY): cv.templatable(cv.boolean),
})


@ACTION_REGISTRY.register('climate.control', CLIMATE_CONTROL_ACTION_SCHEMA)
def climate_control_to_code(config, action_id, template_arg, args):
    var = yield cg.get_variable(config[CONF_ID])
    type = ControlAction.template(template_arg)
    rhs = type.new(var)
    action = cg.Pvariable(action_id, rhs, type=type)
    if CONF_MODE in config:
        template_ = yield cg.templatable(config[CONF_MODE], args, ClimateMode,
                                         to_exp=CLIMATE_MODES)
        cg.add(action.set_mode(template_))
    if CONF_TARGET_TEMPERATURE in config:
        template_ = yield cg.templatable(config[CONF_TARGET_TEMPERATURE], args, float)
        cg.add(action.set_target_temperature(template_))
    if CONF_TARGET_TEMPERATURE_LOW in config:
        template_ = yield cg.templatable(config[CONF_TARGET_TEMPERATURE_LOW], args, float)
        cg.add(action.set_target_temperature_low(template_))
    if CONF_TARGET_TEMPERATURE_HIGH in config:
        template_ = yield cg.templatable(config[CONF_TARGET_TEMPERATURE_HIGH], args, float)
        cg.add(action.set_target_temperature_high(template_))
    if CONF_AWAY in config:
        template_ = yield cg.templatable(config[CONF_AWAY], args, bool)
        cg.add(action.set_away(template_))
    yield action


def to_code(config):
    cg.add_define('USE_CLIMATE')
    cg.add_global(climate_ns.using)
