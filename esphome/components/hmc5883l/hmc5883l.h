#pragma once

#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/i2c/i2c.h"

namespace esphome {
namespace hmc5883l {

enum HMC5883LRange {
  HMC5883L_RANGE_88_UT = 0b000,
  HMC5883L_RANGE_130_UT = 0b001,
  HMC5883L_RANGE_190_UT = 0b010,
  HMC5883L_RANGE_250_UT = 0b011,
  HMC5883L_RANGE_400_UT = 0b100,
  HMC5883L_RANGE_470_UT = 0b101,
  HMC5883L_RANGE_560_UT = 0b110,
  HMC5883L_RANGE_810_UT = 0b111,
};

class HMC5883LComponent : public PollingComponent, public i2c::I2CDevice {
 public:
  HMC5883LComponent(uint32_t update_interval) : PollingComponent(update_interval) {}

  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override;
  void update() override;

  void set_range(HMC5883LRange range) { range_ = range; }
  void set_x_sensor(sensor::Sensor *x_sensor) { x_sensor_ = x_sensor; }
  void set_y_sensor(sensor::Sensor *y_sensor) { y_sensor_ = y_sensor; }
  void set_z_sensor(sensor::Sensor *z_sensor) { z_sensor_ = z_sensor; }
  void set_heading_sensor(sensor::Sensor *heading_sensor) { heading_sensor_ = heading_sensor; }

 protected:
  HMC5883LRange range_{HMC5883L_RANGE_130_UT};
  sensor::Sensor *x_sensor_;
  sensor::Sensor *y_sensor_;
  sensor::Sensor *z_sensor_;
  sensor::Sensor *heading_sensor_;
  enum ErrorCode {
    NONE = 0,
    COMMUNICATION_FAILED,
    ID_REGISTERS,
  } error_code_;
};

}  // namespace hmc5883l
}  // namespace esphome
