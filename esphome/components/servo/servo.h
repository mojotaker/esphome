#pragma once

#include "esphome/core/component.h"
#include "esphome/core/automation.h"
#include "esphome/core/helpers.h"
#include "esphome/core/preferences.h"
#include "esphome/components/output/float_output.h"

namespace esphome {
namespace servo {

extern uint32_t global_servo_id;

class Servo : public Component {
 public:
  Servo(output::FloatOutput *output) : output_(output) {}
  void write(float value) {
    value = clamp(value, -1.0f, 1.0f);

    float level;
    if (value < 0.0)
      level = lerp(this->idle_level_, this->min_level_, -value);
    else
      level = lerp(this->idle_level_, this->max_level_, value);

    this->output_->set_level(level);
    this->save_level_(level);
  }
  void detach() {
    this->output_->set_level(0.0f);
    this->save_level_(0.0f);
  }
  void setup() override {
    float v;
    if (this->restore_) {
      this->rtc_ = global_preferences.make_preference<float>(global_servo_id);
      global_servo_id++;
      if (this->rtc_.load(&v)) {
        this->write(v);
        return;
      }
    }
    this->write(0.0f);
  }
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::DATA; }
  void set_min_level(float min_level) { min_level_ = min_level; }
  void set_idle_level(float idle_level) { idle_level_ = idle_level; }
  void set_max_level(float max_level) { max_level_ = max_level; }

 protected:
  void save_level_(float v) { this->rtc_.save(&v); }

  output::FloatOutput *output_;
  float min_level_ = 0.0300f;
  float idle_level_ = 0.0750f;
  float max_level_ = 0.1200f;
  bool restore_{false};
  ESPPreferenceObject rtc_;
};

template<typename... Ts> class ServoWriteAction : public Action<Ts...> {
 public:
  ServoWriteAction(Servo *servo) : servo_(servo) {}
  TEMPLATABLE_VALUE(float, value)
  void play(Ts... x) override {
    this->servo_->write(this->value_.value(x...));
    this->play_next(x...);
  }

 protected:
  Servo *servo_;
};

template<typename... Ts> class ServoDetachAction : public Action<Ts...> {
 public:
  ServoDetachAction(Servo *servo) : servo_(servo) {}
  void play(Ts... x) override {
    this->servo_->detach();
    this->play_next(x...);
  }

 protected:
  Servo *servo_;
};

}  // namespace servo
}  // namespace esphome
