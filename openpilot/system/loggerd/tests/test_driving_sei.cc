#include <cassert>
#include <fstream>
#include <iterator>
#include <iostream>
#include "system/loggerd/driving_sei.h"

int main(int argc, char **argv) {
  using namespace formosa;
  DrivingTelemetry history;
  history.add_car({1000000000, true, 20, -31.5, .3, .1, true, false, true});
  history.add_control({1000000000, true, true, true, false});
  auto first = history.payload(1000000000, 10);
  assert(first.find("\"speed_mps\":20.0000") != std::string::npos);
  assert(first.find("\"lateral_active\":true") != std::string::npos);
  assert(first.find("\"longitudinal_active\":false") != std::string::npos);
  assert(history.payload(999999999, 9).find("\"speed_mps\":null") != std::string::npos);
  assert(history.payload(1250000000, 11).find("\"speed_mps\":20.0000") != std::string::npos);
  assert(history.payload(1250000001, 12).find("\"speed_mps\":null") != std::string::npos);
  history.add_car({1050000000, false});
  assert(history.payload(1100000000, 13).find("\"cruise_enabled\":null") != std::string::npos);
  history.add_car({1020000000, true, 21, 1, 0, 0});  // out of order, before invalid sample
  assert(history.payload(1040000000, 14).find("\"speed_mps\":21.0000") != std::string::npos);
  history.add_car({1200000000, true, NAN, 0, 0, 0});
  assert(history.payload(1200000000, 15).find("\"speed_mps\":null") != std::string::npos);
  for (uint64_t i = 1; i <= 1000; ++i) history.add_car({2000000000 + i, true, 10, 0, 0, 0});
  assert(history.payload(2000000001, 16).find("\"speed_mps\":null") != std::string::npos);
  const std::vector<uint8_t> au{0,0,0,1,0x46,1,0x50,0,0,1,0x26,1,0x55};
  auto annotated = embed_driving_sei(au.data(), au.size(), first, true);
  assert(std::equal(au.begin(), au.begin()+7, annotated.begin()));  // AUD stays first
  assert(std::equal(au.begin()+7, au.end(), annotated.end()-(au.size()-7)));
  assert(annotated[11] == 0x4e && annotated[12] == 1 && annotated[13] == 5);
  const uint8_t invalid[] = {1,2,3,4};
  assert(embed_driving_sei(invalid, 4, first, false).empty());
  assert(embed_driving_sei(nullptr, 0, first, false).empty());
  assert(driving_sei(std::string(2049,'x'),true).empty());
  const auto escaped = driving_sei(std::string("\0\0\1\0\0\2",6),false);
  const uint8_t prevention[] = {0,0,3,1,0,0,3,2};
  assert(std::search(escaped.begin()+4,escaped.end(),std::begin(prevention),std::end(prevention)) != escaped.end());
  for (size_t i=6;i+2<escaped.size();++i) assert(!(escaped[i]==0&&escaped[i+1]==0&&escaped[i+2]<=2));
  // Optional real-codec fixture injection; preserve every original NAL byte.
  if (argc == 4) {
    std::ifstream in(argv[1],std::ios::binary);
    std::vector<uint8_t> data((std::istreambuf_iterator<char>(in)),{});
    const bool hevc=std::string(argv[3])=="hevc";
    std::vector<size_t> offsets;
    for(size_t i=0;i+4<data.size();++i){
      size_t header=0;
      if(data[i]==0&&data[i+1]==0&&data[i+2]==0&&data[i+3]==1)header=4;
      else if(data[i]==0&&data[i+1]==0&&data[i+2]==1)header=3;
      if(header){const int type=hevc?(data[i+header]>>1)&63:data[i+header]&31;
        if(type==(hevc?35:9))offsets.push_back(i);
        i+=header-1;}
    }
    assert(!offsets.empty());offsets.push_back(data.size());
    std::ofstream file(argv[2],std::ios::binary);
    file.write(reinterpret_cast<char *>(data.data()),offsets[0]);
    DrivingTelemetry fixture;
    for(size_t i=0;i+1<offsets.size();++i){
      uint64_t t=1000000000+i*50000000;
      fixture.add_car({t,true,20.+i*.1,-31.5+i,.3,.1,true,false,true});
      fixture.add_control({t,true,true,true,i%2==0});
      auto out=embed_driving_sei(data.data()+offsets[i],offsets[i+1]-offsets[i],fixture.payload(t,i),hevc);
      assert(!out.empty());file.write(reinterpret_cast<char *>(out.data()),out.size());
    }
  }
  std::cout << "Driving SEI causal, expiry, invalidation, bounds and NAL checks passed\n";
}
