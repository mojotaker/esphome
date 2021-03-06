import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c, sensor
from esphome.const import CONF_ID, CONF_TEMPERATURE, \
    CONF_UPDATE_INTERVAL, ICON_BRIEFCASE_DOWNLOAD, UNIT_METER_PER_SECOND_SQUARED, \
    ICON_SCREEN_ROTATION, UNIT_DEGREE_PER_SECOND, ICON_THERMOMETER, UNIT_CELSIUS

DEPENDENCIES = ['i2c']

CONF_ACCEL_X = 'accel_x'
CONF_ACCEL_Y = 'accel_y'
CONF_ACCEL_Z = 'accel_z'
CONF_GYRO_X = 'gyro_x'
CONF_GYRO_Y = 'gyro_y'
CONF_GYRO_Z = 'gyro_z'

mpu6050_ns = cg.esphome_ns.namespace('mpu6050')
MPU6050Component = mpu6050_ns.class_('MPU6050Component', cg.PollingComponent, i2c.I2CDevice)

accel_schema = sensor.sensor_schema(UNIT_METER_PER_SECOND_SQUARED, ICON_BRIEFCASE_DOWNLOAD, 2)
gyro_schema = sensor.sensor_schema(UNIT_DEGREE_PER_SECOND, ICON_SCREEN_ROTATION, 2)
temperature_schema = sensor.sensor_schema(UNIT_CELSIUS, ICON_THERMOMETER, 1)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_variable_id(MPU6050Component),
    cv.Optional(CONF_ACCEL_X): cv.nameable(accel_schema),
    cv.Optional(CONF_ACCEL_Y): cv.nameable(accel_schema),
    cv.Optional(CONF_ACCEL_Z): cv.nameable(accel_schema),
    cv.Optional(CONF_GYRO_X): cv.nameable(gyro_schema),
    cv.Optional(CONF_GYRO_Y): cv.nameable(gyro_schema),
    cv.Optional(CONF_GYRO_Z): cv.nameable(gyro_schema),
    cv.Optional(CONF_TEMPERATURE): cv.nameable(temperature_schema),
    cv.Optional(CONF_UPDATE_INTERVAL, default='60s'): cv.update_interval,
}).extend(cv.COMPONENT_SCHEMA).extend(i2c.i2c_device_schema(0x68))


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_UPDATE_INTERVAL])
    yield cg.register_component(var, config)
    yield i2c.register_i2c_device(var, config)

    for d in ['x', 'y', 'z']:
        accel_key = 'accel_{}'.format(d)
        if accel_key in config:
            sens = yield sensor.new_sensor(config[accel_key])
            cg.add(getattr(var, 'set_accel_{}_sensor'.format(d))(sens))
        accel_key = 'gyro_{}'.format(d)
        if accel_key in config:
            sens = yield sensor.new_sensor(config[accel_key])
            cg.add(getattr(var, 'set_gyro_{}_sensor'.format(d))(sens))

    if CONF_TEMPERATURE in config:
        sens = yield sensor.new_sensor(config[CONF_TEMPERATURE])
        cg.add(var.set_temperature_sensor(sens))
