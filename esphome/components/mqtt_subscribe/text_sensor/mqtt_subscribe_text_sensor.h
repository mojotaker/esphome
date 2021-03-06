#pragma once

#include "esphome/core/component.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/mqtt/mqtt_client.h"

namespace esphome {
namespace mqtt_subscribe {

class MQTTSubscribeTextSensor : public text_sensor::TextSensor, public Component {
 public:
  MQTTSubscribeTextSensor(const std::string &name, mqtt::MQTTClientComponent *parent, const std::string &topic)
      : TextSensor(name), parent_(parent), topic_(topic) {}

  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override;
  void set_qos(uint8_t qos);

 protected:
  mqtt::MQTTClientComponent *parent_;
  std::string topic_;
  uint8_t qos_{};
};

}  // namespace mqtt_subscribe
}  // namespace esphome
