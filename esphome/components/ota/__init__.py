import logging

import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_ID, CONF_PASSWORD, CONF_PORT, CONF_SAFE_MODE
from esphome.core import CORE, coroutine_with_priority

_LOGGER = logging.getLogger(__name__)

ota_ns = cg.esphome_ns.namespace('ota')
OTAComponent = ota_ns.class_('OTAComponent', cg.Component)


CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_variable_id(OTAComponent),
    cv.Optional(CONF_SAFE_MODE, default=True): cv.boolean,
    cv.SplitDefault(CONF_PORT, esp8266=8266, esp32=3232): cv.port,
    cv.Optional(CONF_PASSWORD, default=''): cv.string,
}).extend(cv.COMPONENT_SCHEMA)


@coroutine_with_priority(50.0)
def to_code(config):
    ota = cg.new_Pvariable(config[CONF_ID], config[CONF_PORT])
    cg.add(ota.set_auth_password(config[CONF_PASSWORD]))
    if config[CONF_SAFE_MODE]:
        cg.add(ota.start_safe_mode())

    if CORE.is_esp8266:
        cg.add_library('Update', None)
    elif CORE.is_esp32:
        cg.add_library('Hash', None)

    # Register at end for safe mode
    yield cg.register_component(ota, config)
