import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import lcd_base, i2c
from esphome.const import CONF_ID, CONF_UPDATE_INTERVAL

DEPENDENCIES = ['i2c']
AUTO_LOAD = ['lcd_base']

lcd_pcf8574_ns = cg.esphome_ns.namespace('lcd_pcf8574')
PCF8574LCDDisplay = lcd_pcf8574_ns.class_('PCF8574LCDDisplay', lcd_base.LCDDisplay, i2c.I2CDevice)

CONFIG_SCHEMA = lcd_base.LCD_SCHEMA.extend({
    cv.GenerateID(): cv.declare_variable_id(PCF8574LCDDisplay),
}).extend(i2c.i2c_device_schema(0x3F))


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_UPDATE_INTERVAL])
    yield lcd_base.setup_lcd_display(var, config)
    yield i2c.register_i2c_device(var, config)
