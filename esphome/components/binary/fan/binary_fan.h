#pragma once

#include "esphome/core/component.h"
#include "esphome/components/output/binary_output.h"
#include "esphome/components/fan/fan_state.h"

namespace esphome {
namespace binary {

class BinaryFan : public Component {
 public:
  BinaryFan(fan::FanState *fan, output::BinaryOutput *output) : fan_(fan), output_(output) {}
  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override;
  void set_oscillating(output::BinaryOutput *oscillating) { this->oscillating_ = oscillating; }

 protected:
  fan::FanState *fan_;
  output::BinaryOutput *output_;
  output::BinaryOutput *oscillating_{nullptr};
  bool next_update_{true};
};

}  // namespace binary
}  // namespace esphome
