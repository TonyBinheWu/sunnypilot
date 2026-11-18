#pragma once

#include <algorithm>
#include <cstdint>
#include <string>

struct CarrotVisionResolution {
  int width;
  int height;
  int bitrate;
};

// Only the dedicated Carrot Vision encoder uses these profiles. Four-pixel
// alignment is accepted by VIDC; preserve aspect and never upscale the source.
inline CarrotVisionResolution carrot_vision_resolution(const std::string &mode, int source_width, int source_height, int base_bitrate) {
  int height = mode == "360" ? 360 : mode == "540" ? 540 : mode == "720" ? 720 : 0;
  // 964x604 was half an AR/OX frame, but stretches C4's OS04C10 frames.
  // Keep the whole source frame and its aspect for calibrated projection.
  if (height == 0) return {std::max(4, source_width / 8 * 4), std::max(4, source_height / 8 * 4), base_bitrate};
  height = std::max(4, std::min(height, source_height) / 4 * 4);
  const int width = std::max(4, std::min(source_width, source_width * height / source_height) / 4 * 4);
  const int bitrate = std::clamp<int64_t>(int64_t(base_bitrate) * width * height / (964 * 604), 200000, 4000000);
  return {width, height, bitrate};
}
