import logging
import os
import re

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation, pins
from esphome.const import ARDUINO_VERSION_ESP32_DEV, ARDUINO_VERSION_ESP8266_DEV, \
    CONF_ARDUINO_VERSION, CONF_BOARD, CONF_BOARD_FLASH_MODE, CONF_BUILD_PATH, \
    CONF_ESPHOME, CONF_INCLUDES, CONF_LIBRARIES, \
    CONF_NAME, CONF_ON_BOOT, CONF_ON_LOOP, CONF_ON_SHUTDOWN, CONF_PLATFORM, \
    CONF_PLATFORMIO_OPTIONS, CONF_PRIORITY, CONF_TRIGGER_ID, \
    CONF_ESP8266_RESTORE_FROM_FLASH, __version__, ARDUINO_VERSION_ESP8266_2_3_0, \
    ARDUINO_VERSION_ESP8266_2_5_0
from esphome.core import CORE, EsphomeError, coroutine_with_priority
from esphome.pins import ESP8266_FLASH_SIZES, ESP8266_LD_SCRIPTS
from esphome.py_compat import text_type

_LOGGER = logging.getLogger(__name__)

BUILD_FLASH_MODES = ['qio', 'qout', 'dio', 'dout']
StartupTrigger = cg.esphome_ns.StartupTrigger
ShutdownTrigger = cg.esphome_ns.ShutdownTrigger
LoopTrigger = cg.esphome_ns.LoopTrigger

VERSION_REGEX = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+(?:[ab]\d+)?$')


def validate_board(value):
    if CORE.is_esp8266:
        board_pins = pins.ESP8266_BOARD_PINS
    elif CORE.is_esp32:
        board_pins = pins.ESP32_BOARD_PINS
    else:
        raise NotImplementedError

    if value not in board_pins:
        raise cv.Invalid(u"Could not find board '{}'. Valid boards are {}".format(
            value, u', '.join(pins.ESP8266_BOARD_PINS.keys())))
    return value


validate_platform = cv.one_of('ESP32', 'ESP8266', upper=True)


PLATFORMIO_ESP8266_LUT = {
    '2.5.0': 'espressif8266@2.0.1',
    '2.4.2': 'espressif8266@1.8.0',
    '2.4.1': 'espressif8266@1.7.3',
    '2.4.0': 'espressif8266@1.6.0',
    '2.3.0': 'espressif8266@1.5.0',
    'RECOMMENDED': 'espressif8266@1.8.0',
    'LATEST': 'espressif8266',
    'DEV': ARDUINO_VERSION_ESP8266_DEV,
}

PLATFORMIO_ESP32_LUT = {
    '1.0.0': 'espressif32@1.4.0',
    '1.0.1': 'espressif32@1.6.0',
    'RECOMMENDED': 'espressif32@1.6.0',
    'LATEST': 'espressif32',
    'DEV': ARDUINO_VERSION_ESP32_DEV,
}


def validate_arduino_version(value):
    value = cv.string_strict(value)
    value_ = value.upper()
    if CORE.is_esp8266:
        if VERSION_REGEX.match(value) is not None and value_ not in PLATFORMIO_ESP8266_LUT:
            raise cv.Invalid("Unfortunately the arduino framework version '{}' is unsupported "
                             "at this time. You can override this by manually using "
                             "espressif8266@<platformio version>")
        if value_ in PLATFORMIO_ESP8266_LUT:
            return PLATFORMIO_ESP8266_LUT[value_]
        return value
    if CORE.is_esp32:
        if VERSION_REGEX.match(value) is not None and value_ not in PLATFORMIO_ESP32_LUT:
            raise cv.Invalid("Unfortunately the arduino framework version '{}' is unsupported "
                             "at this time. You can override this by manually using "
                             "espressif32@<platformio version>")
        if value_ in PLATFORMIO_ESP32_LUT:
            return PLATFORMIO_ESP32_LUT[value_]
        return value
    raise NotImplementedError


def default_build_path():
    return CORE.name


CONFIG_SCHEMA = cv.Schema({
    cv.Required(CONF_NAME): cv.valid_name,
    cv.Required(CONF_PLATFORM): cv.one_of('ESP8266', 'ESP32', 'ESPRESSIF32',
                                          upper=True),
    cv.Required(CONF_BOARD): validate_board,
    cv.Optional(CONF_ARDUINO_VERSION, default='recommended'): validate_arduino_version,
    cv.Optional(CONF_BUILD_PATH, default=default_build_path): cv.string,
    cv.Optional(CONF_PLATFORMIO_OPTIONS, default={}): cv.Schema({
        cv.string_strict: cv.Any([cv.string], cv.string),
    }),
    cv.SplitDefault(CONF_ESP8266_RESTORE_FROM_FLASH, esp8266=False): cv.All(cv.only_on_esp8266,
                                                                            cv.boolean),

    cv.SplitDefault(CONF_BOARD_FLASH_MODE, esp8266='dout'): cv.one_of(*BUILD_FLASH_MODES,
                                                                      lower=True),
    cv.Optional(CONF_ON_BOOT): automation.validate_automation({
        cv.GenerateID(CONF_TRIGGER_ID): cv.declare_variable_id(StartupTrigger),
        cv.Optional(CONF_PRIORITY): cv.float_,
    }),
    cv.Optional(CONF_ON_SHUTDOWN): automation.validate_automation({
        cv.GenerateID(CONF_TRIGGER_ID): cv.declare_variable_id(ShutdownTrigger),
    }),
    cv.Optional(CONF_ON_LOOP): automation.validate_automation({
        cv.GenerateID(CONF_TRIGGER_ID): cv.declare_variable_id(LoopTrigger),
    }),
    cv.Optional(CONF_INCLUDES, default=[]): cv.ensure_list(cv.file_),
    cv.Optional(CONF_LIBRARIES, default=[]): cv.ensure_list(cv.string_strict),
})


def preload_core_config(config):
    if 'esphomeyaml' in config:
        _LOGGER.warning("The esphomeyaml section has been renamed to esphome in 1.11.0. "
                        "Please replace 'esphomeyaml:' in your configuration with 'esphome:'.")
        config[CONF_ESPHOME] = config.pop('esphomeyaml')
    if CONF_ESPHOME not in config:
        raise EsphomeError(u"No esphome section in config")
    core_conf = config[CONF_ESPHOME]
    if CONF_PLATFORM not in core_conf:
        raise EsphomeError("esphome.platform not specified.")
    if CONF_BOARD not in core_conf:
        raise EsphomeError("esphome.board not specified.")
    if CONF_NAME not in core_conf:
        raise EsphomeError("esphome.name not specified.")

    try:
        CORE.esp_platform = validate_platform(core_conf[CONF_PLATFORM])
        CORE.board = validate_board(core_conf[CONF_BOARD])
        CORE.name = cv.valid_name(core_conf[CONF_NAME])
        CORE.build_path = CORE.relative_path(
            cv.string(core_conf.get(CONF_BUILD_PATH, default_build_path())))
    except cv.Invalid as e:
        raise EsphomeError(text_type(e))


@coroutine_with_priority(-1000.0)
def add_includes(includes):
    # Add includes at the very end, so that the included files can access global variables
    for include in includes:
        path = CORE.relative_path(include)
        res = os.path.relpath(path, CORE.relative_build_path('src'))
        cg.add_global(cg.RawExpression(u'#include "{}"'.format(res)))


@coroutine_with_priority(100.0)
def to_code(config):
    cg.add_global(cg.global_ns.namespace('esphome').using)
    cg.add_define('ESPHOME_VERSION', __version__)
    cg.add(cg.App.pre_setup(config[CONF_NAME], cg.RawExpression('__DATE__ ", " __TIME__')))

    for conf in config.get(CONF_ON_BOOT, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], conf.get(CONF_PRIORITY))
        yield cg.register_component(trigger, conf)
        yield automation.build_automation(trigger, [], conf)

    for conf in config.get(CONF_ON_SHUTDOWN, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID])
        yield cg.register_component(trigger, conf)
        yield automation.build_automation(trigger, [], conf)

    for conf in config.get(CONF_ON_LOOP, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID])
        yield cg.register_component(trigger, conf)
        yield automation.build_automation(trigger, [], conf)

    # Build flags
    if CORE.is_esp8266 and CORE.board in ESP8266_FLASH_SIZES and \
            CORE.arduino_version != ARDUINO_VERSION_ESP8266_2_3_0:
        flash_size = ESP8266_FLASH_SIZES[CORE.board]
        ld_scripts = ESP8266_LD_SCRIPTS[flash_size]
        ld_script = None

        if CORE.arduino_version in ('espressif8266@1.8.0', 'espressif8266@1.7.3',
                                    'espressif8266@1.6.0'):
            ld_script = ld_scripts[0]
        elif CORE.arduino_version in (ARDUINO_VERSION_ESP8266_DEV, ARDUINO_VERSION_ESP8266_2_5_0):
            ld_script = ld_scripts[1]

        if ld_script is not None:
            cg.add_build_flag('-Wl,-T{}'.format(ld_script))

    if CORE.is_esp8266 and CORE.arduino_version in (ARDUINO_VERSION_ESP8266_DEV,
                                                    ARDUINO_VERSION_ESP8266_2_5_0):
        cg.add_build_flag('-fno-exceptions')

    # Libraries
    if CORE.is_esp32:
        cg.add_library('Preferences', None)
        cg.add_library('ESPmDNS', None)
    elif CORE.is_esp8266:
        cg.add_library('ESP8266WiFi', None)
        cg.add_library('ESP8266mDNS', None)

    for lib in config[CONF_LIBRARIES]:
        if '@' in lib:
            name, vers = lib.split('@', 1)
            cg.add_library(name, vers)
        else:
            cg.add_library(lib, None)

    cg.add_build_flag('-Wno-unused-variable')
    cg.add_build_flag('-Wno-unused-but-set-variable')
    cg.add_build_flag('-Wno-sign-compare')
    if config.get(CONF_ESP8266_RESTORE_FROM_FLASH, False):
        cg.add_define('USE_ESP8266_PREFERENCES_FLASH')

    if config[CONF_INCLUDES]:
        CORE.add_job(add_includes, config[CONF_INCLUDES])
