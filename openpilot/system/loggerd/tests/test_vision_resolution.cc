#include <cassert>
#include <cmath>
#include "system/loggerd/vision_resolution.h"

int main() {
  for (auto mode : {"standard", "bad", ""}) {
    auto size = carrot_vision_resolution(mode, 1344, 760, 600000);
    assert(size.width == 964 && size.height == 604 && size.bitrate == 600000);
  }
  for (auto source : {std::pair{1344, 760}, std::pair{1928, 1208}, std::pair{640, 480}}) {
    for (auto mode : {"360", "540", "720"}) {
      auto size = carrot_vision_resolution(mode, source.first, source.second, 600000);
      assert(size.width <= source.first && size.height <= source.second);
      assert(size.width % 4 == 0 && size.height % 4 == 0);
      assert(std::abs(double(size.width) / size.height - double(source.first) / source.second) < .012);
      assert(size.bitrate >= 200000 && size.bitrate <= 4000000);
    }
  }
  auto low = carrot_vision_resolution("360", 1344, 760, 600000);
  auto high = carrot_vision_resolution("720", 1344, 760, 600000);
  assert(low.bitrate < high.bitrate && low.width < high.width && low.height < high.height);
}
