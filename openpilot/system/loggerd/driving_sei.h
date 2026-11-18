#pragma once

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <deque>
#include <iomanip>
#include <locale>
#include <sstream>
#include <string>
#include <vector>

namespace formosa {
// ISO/IEC user_data_unregistered UUID, schema versioned independently of video.
inline constexpr std::array<uint8_t, 16> DRIVE_UUID = {
  0xd1,0x5f,0xb7,0xea,0x55,0x69,0x4b,0xdf,0xa6,0x40,0x4f,0x52,0x4d,0x4f,0x53,0x41};

struct CarSample {
  uint64_t time = 0;
  bool valid = false;
  double speed = 0, steering = 0, gas = 0, brake = 0;
  bool gas_pressed = false, brake_pressed = false, cruise_enabled = false;
};
struct ControlSample {
  uint64_t time = 0;
  bool valid = false, enabled = false, lateral = false, longitudinal = false;
};

class DrivingTelemetry {
  std::deque<CarSample> cars;
  std::deque<ControlSample> controls;
  static constexpr uint64_t MAX_AGE = 250000000;  // 250 ms, never future samples
  template <class T> static void add(std::deque<T> &history, const T &sample) {
    auto at = std::upper_bound(history.begin(), history.end(), sample.time,
                              [](uint64_t t, const T &value) { return t < value.time; });
    history.insert(at, sample);
    while (history.size() > 512) history.pop_front();
  }
  template <class T> static const T *at(const std::deque<T> &history, uint64_t time) {
    auto it = std::upper_bound(history.begin(), history.end(), time,
                              [](uint64_t t, const T &value) { return t < value.time; });
    if (it == history.begin()) return nullptr;
    const T &sample = *--it;
    return sample.valid && time - sample.time <= MAX_AGE ? &sample : nullptr;
  }
public:
  void add_car(CarSample sample) {
    sample.valid = sample.valid && std::isfinite(sample.speed) && std::isfinite(sample.steering) &&
      std::isfinite(sample.gas) && std::isfinite(sample.brake) && sample.speed >= 0 && sample.speed <= 150 &&
      std::abs(sample.steering) <= 3000 && sample.gas >= 0 && sample.gas <= 1 && sample.brake >= 0 && sample.brake <= 1;
    add(cars, sample);
  }
  void add_control(const ControlSample &sample) { add(controls, sample); }
  std::string payload(uint64_t frame_time, uint32_t frame_id) const {
    const CarSample *car = at(cars, frame_time);
    const ControlSample *control = at(controls, frame_time);
    std::ostringstream out; out.imbue(std::locale::classic()); out << std::fixed << std::setprecision(4);
    out << "{\"schema\":\"formosa.drive.v1\",\"frame_id\":" << frame_id << ",\"frame_mono_ns\":" << frame_time;
    out << ",\"car_mono_ns\":" << (car ? std::to_string(car->time) : "null");
    out << ",\"control_mono_ns\":" << (control ? std::to_string(control->time) : "null");
    auto number = [&](const char *key, double value) { out << ",\"" << key << "\":"; if (car) out << value; else out << "null"; };
    auto flag = [&](const char *key, bool valid, bool value) { out << ",\"" << key << "\":" << (valid ? (value ? "true" : "false") : "null"); };
    number("speed_mps", car ? car->speed : 0); number("steering_angle_deg", car ? car->steering : 0);
    number("gas", car ? car->gas : 0); number("brake", car ? car->brake : 0);
    flag("gas_pressed", car, car && car->gas_pressed); flag("brake_pressed", car, car && car->brake_pressed);
    flag("cruise_enabled", car, car && car->cruise_enabled);
    flag("control_enabled", control, control && control->enabled);
    flag("lateral_active", control, control && control->lateral);
    flag("longitudinal_active", control, control && control->longitudinal);
    out << '}'; return out.str();
  }
};

inline std::vector<uint8_t> driving_sei(const std::string &json, bool hevc) {
  if (json.empty() || json.size() > 2048) return {};
  std::vector<uint8_t> rbsp{5};  // payloadType user_data_unregistered
  size_t size = DRIVE_UUID.size() + json.size();
  while (size >= 255) { rbsp.push_back(255); size -= 255; }
  rbsp.push_back(size);
  rbsp.insert(rbsp.end(), DRIVE_UUID.begin(), DRIVE_UUID.end());
  rbsp.insert(rbsp.end(), json.begin(), json.end());
  rbsp.push_back(0x80);  // rbsp_trailing_bits
  std::vector<uint8_t> nal{0,0,0,1};
  if (hevc) { nal.push_back(39 << 1); nal.push_back(1); } else { nal.push_back(6); }
  int zeros = 0;
  for (uint8_t byte : rbsp) {
    if (zeros >= 2 && byte <= 3) { nal.push_back(3); zeros = 0; }
    nal.push_back(byte); zeros = byte == 0 ? zeros + 1 : 0;
  }
  return nal;
}

inline std::vector<uint8_t> embed_driving_sei(const uint8_t *data, size_t size, const std::string &json, bool hevc) {
  auto prefix = [&](size_t i) -> size_t {
    if (i + 3 <= size && data[i] == 0 && data[i+1] == 0 && data[i+2] == 1) return 3;
    if (i + 4 <= size && data[i] == 0 && data[i+1] == 0 && data[i+2] == 0 && data[i+3] == 1) return 4;
    return 0;
  };
  if (!data || !prefix(0) || size < prefix(0) + (hevc ? 2 : 1)) return {};
  size_t insertion = 0, header = prefix(0);
  const int type = hevc ? (data[header] >> 1) & 63 : data[header] & 31;
  // An access-unit delimiter must stay first. No encoded slice is altered.
  if (type == (hevc ? 35 : 9)) {
    insertion = header + (hevc ? 2 : 1);
    while (insertion < size && !prefix(insertion)) ++insertion;
  }
  auto sei = driving_sei(json, hevc);
  if (sei.empty()) return {};
  std::vector<uint8_t> result; result.reserve(size + sei.size());
  result.insert(result.end(), data, data + insertion);
  result.insert(result.end(), sei.begin(), sei.end());
  result.insert(result.end(), data + insertion, data + size);
  return result;
}
}  // namespace formosa
