#pragma once

#include "esphome/core/component.h"
#include "esphome/core/esphal.h"
#include "esphome/components/stepper/stepper.h"

namespace esphome {
namespace uln2003 {

enum ULN2003StepMode {
  ULN2003_STEP_MODE_FULL_STEP,
  ULN2003_STEP_MODE_HALF_STEP,
  ULN2003_STEP_MODE_WAVE_DRIVE,
};

class ULN2003 : public stepper::Stepper, public Component {
 public:
  ULN2003(GPIOPin *pin_a, GPIOPin *pin_b, GPIOPin *pin_c, GPIOPin *pin_d)
      : pin_a_(pin_a), pin_b_(pin_b), pin_c_(pin_c), pin_d_(pin_d) {}

  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::HARDWARE; }
  void set_sleep_when_done(bool sleep_when_done) { this->sleep_when_done_ = sleep_when_done; }
  void set_step_mode(ULN2003StepMode step_mode) { this->step_mode_ = step_mode; }

 protected:
  void write_step_(int32_t step);

  bool sleep_when_done_{false};
  GPIOPin *pin_a_;
  GPIOPin *pin_b_;
  GPIOPin *pin_c_;
  GPIOPin *pin_d_;
  ULN2003StepMode step_mode_{ULN2003_STEP_MODE_FULL_STEP};
  HighFrequencyLoopRequester high_freq_;
  int32_t current_uln_pos_{0};
};

}  // namespace uln2003
}  // namespace esphome
