#pragma once

#include "esphome/core/component.h"
#include "esphome/components/output/float_output.h"
#include "esphome/components/light/light_output.h"

namespace esphome {
namespace monochromatic {

class MonochromaticLightOutput : public light::LightOutput {
 public:
  MonochromaticLightOutput(output::FloatOutput *output) : output_(output) {}
  light::LightTraits get_traits() override {
    auto traits = light::LightTraits();
    traits.set_supports_brightness(true);
    return traits;
  }
  void write_state(light::LightState *state) override {
    float bright;
    state->current_values_as_brightness(&bright);
    this->output_->set_level(bright);
  }

 protected:
  output::FloatOutput *output_;
};

}  // namespace monochromatic
}  // namespace esphome
