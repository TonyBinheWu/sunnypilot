// Small local-file demux/remux helper. No video decoding or network protocols.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <string>
#include <sys/stat.h>
extern "C" {
#include <libavformat/avformat.h>
#include <libavutil/avutil.h>
}

static size_t prefix(const uint8_t *p, size_t n, size_t i) {
  if(i+4<=n&&p[i]==0&&p[i+1]==0&&p[i+2]==0&&p[i+3]==1)return 4;
  if(i+3<=n&&p[i]==0&&p[i+1]==0&&p[i+2]==1)return 3;
  return 0;
}
static void emit_nal(const uint8_t *p,size_t n,bool hevc,double pts) {
  if(n<2||n>8192)return;
  int type=hevc?(p[0]>>1)&63:p[0]&31;
  if(hevc?(type!=39&&type!=40):type!=6)return;
  constexpr char hex[]="0123456789abcdef";
  std::string data;data.reserve(n*2);
  for(size_t i=0;i<n;++i){data.push_back(hex[p[i]>>4]);data.push_back(hex[p[i]&15]);}
  std::cout<<std::fixed<<std::setprecision(9)<<pts<<'\t'<<(hevc?"hevc":"h264")<<'\t'<<data<<'\n';
}
static void inspect(const AVPacket *pkt,bool hevc,int length_size,double pts) {
  const uint8_t *p=pkt->data;size_t n=pkt->size;
  if(length_size){
    for(size_t at=0;at+length_size<=n;){
      size_t size=0;for(int i=0;i<length_size;++i)size=(size<<8)|p[at++];
      if(!size||size>n-at)return;
      emit_nal(p+at,size,hevc,pts);at+=size;
    }
  }else{
    for(size_t at=0;at<n;){
      size_t start=prefix(p,n,at);if(!start){++at;continue;}
      at+=start;size_t end=at;while(end<n&&!prefix(p,n,end))++end;
      emit_nal(p+at,end-at,hevc,pts);at=end;
    }
  }
}
int main(int argc,char **argv) {
  bool remux=argc==4&&std::string(argv[1])=="--remux";
  if(!remux&&argc!=2)return 2;
  const char *path=argv[remux?2:1];
  struct stat st{};
  if(stat(path,&st)||!S_ISREG(st.st_mode)||st.st_size>8*1024*1024)return 3;
  AVFormatContext *input=nullptr,*output=nullptr;
  AVDictionary *opts=nullptr;av_dict_set(&opts,"protocol_whitelist","file",0);
  int rc=avformat_open_input(&input,path,nullptr,&opts);av_dict_free(&opts);
  if(rc<0)return 4;
  auto cleanup=[&](){if(output){if(output->pb)avio_closep(&output->pb);avformat_free_context(output);}avformat_close_input(&input);};
  if(avformat_find_stream_info(input,nullptr)<0){cleanup();return 4;}
  int video=av_find_best_stream(input,AVMEDIA_TYPE_VIDEO,-1,-1,nullptr,0);
  if(video<0){cleanup();return 5;}
  auto *stream=input->streams[video];auto *par=stream->codecpar;
  bool hevc=par->codec_id==AV_CODEC_ID_HEVC;
  if(!hevc&&par->codec_id!=AV_CODEC_ID_H264){cleanup();return 5;}
  bool mp4=std::strstr(input->iformat->name,"mov")||std::strstr(input->iformat->name,"mp4");
  int length_size=0;
  if(mp4){int offset=hevc?21:4;if(par->extradata_size<=offset||par->extradata[0]!=1){cleanup();return 5;}length_size=(par->extradata[offset]&3)+1;}
  int64_t origin=(!mp4&&input->start_time!=AV_NOPTS_VALUE)?input->start_time:0;
  if(remux){
    if(avformat_alloc_output_context2(&output,nullptr,"mp4",argv[3])<0||!output){cleanup();return 6;}
    for(unsigned i=0;i<input->nb_streams;++i){
      auto *out=avformat_new_stream(output,nullptr);
      if(!out||avcodec_parameters_copy(out->codecpar,input->streams[i]->codecpar)<0){cleanup();return 6;}
      out->codecpar->codec_tag=0;out->time_base=input->streams[i]->time_base;
    }
    if(avio_open(&output->pb,argv[3],AVIO_FLAG_WRITE)<0){cleanup();return 6;}
    AVDictionary *mux_opts=nullptr;av_dict_set(&mux_opts,"movflags","+faststart",0);
    rc=avformat_write_header(output,&mux_opts);av_dict_free(&mux_opts);
    if(rc<0){cleanup();return 6;}
  }
  AVPacket *pkt=av_packet_alloc();if(!pkt){cleanup();return 7;}
  auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(18);
  int count=0;bool valid=true;
  while((rc=av_read_frame(input,pkt))>=0){
    if(++count>20000||std::chrono::steady_clock::now()>deadline){valid=false;av_packet_unref(pkt);break;}
    auto *in_stream=input->streams[pkt->stream_index];
    if(remux){
      int64_t shift=av_rescale_q(origin,AV_TIME_BASE_Q,in_stream->time_base);
      if(pkt->pts!=AV_NOPTS_VALUE)pkt->pts-=shift;
      if(pkt->dts!=AV_NOPTS_VALUE)pkt->dts-=shift;
      av_packet_rescale_ts(pkt,in_stream->time_base,output->streams[pkt->stream_index]->time_base);
      pkt->pos=-1;
      if(av_interleaved_write_frame(output,pkt)<0){valid=false;av_packet_unref(pkt);break;}
    }else if(pkt->stream_index==video&&pkt->pts!=AV_NOPTS_VALUE){
      double pts=pkt->pts*av_q2d(in_stream->time_base)-origin/double(AV_TIME_BASE);
      if(std::isfinite(pts)&&pts>=0&&pts<=3600)inspect(pkt,hevc,length_size,pts);
    }
    av_packet_unref(pkt);
  }
  if(rc!=AVERROR_EOF&&rc<0)valid=false;
  if(remux&&av_write_trailer(output)<0)valid=false;
  av_packet_free(&pkt);cleanup();return valid?0:8;
}
