#define WIDTH 2048
#define RMS 1
#define EPSILON 1.0000000000e-05f

#pragma clang fp contract(off)
#define DEV __attribute__((device)) __attribute__((always_inline)) inline
typedef unsigned short u16;
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);
DEV float f(u16 x) { return __builtin_bit_cast(float, (unsigned)x << 16); }
DEV u16 b(float x) { unsigned v=__builtin_bit_cast(unsigned,x); return (v+0x7fff+((v>>16)&1))>>16; }
template<int mask> DEV float shuffle(float x) {
  return __builtin_bit_cast(float,__builtin_amdgcn_ds_swizzle(__builtin_bit_cast(int,x),mask));
}
DEV float sum(float x) {
  x+=shuffle<0x401f>(x); x+=shuffle<0x201f>(x); x+=shuffle<0x101f>(x);
  x+=shuffle<0x081f>(x); x+=shuffle<0x041f>(x); return x;
}
DEV void barrier() {
  __builtin_amdgcn_fence(__ATOMIC_RELEASE,"workgroup"); __builtin_amdgcn_s_barrier();
  __builtin_amdgcn_fence(__ATOMIC_ACQUIRE,"workgroup");
}
extern "C" __attribute__((global,amdgpu_flat_work_group_size(256,256)))
void alpamayo_norm(u16 *out,const u16 *x,const u16 *weight,const u16 *bias) {
  int t=__ockl_get_local_id(0), row=__ockl_get_group_id(0), wave=t/32, lane=t%32;
  __attribute__((shared,aligned(16))) float sums[8];
  float mean=0;
  if (!RMS) {
    float v=0; for(int i=t;i<WIDTH;i+=256) v+=f(x[row*WIDTH+i]);
    v=sum(v); if(lane==0) sums[wave]=v; barrier();
    for(int i=0;i<8;i++) mean+=sums[i]; mean/=WIDTH; barrier();
  }
  float squared=0;
  for(int i=t;i<WIDTH;i+=256) { float v=f(x[row*WIDTH+i])-mean; squared+=v*v; }
  squared=sum(squared); if(lane==0) sums[wave]=squared; barrier();
  float variance=0; for(int i=0;i<8;i++) variance+=sums[i]; variance/=WIDTH;
  float inv=__builtin_amdgcn_rsqf(variance+EPSILON);
  for(int i=t;i<WIDTH;i+=256) {
    float normalized=(f(x[row*WIDTH+i])-mean)*inv;
    out[row*WIDTH+i]=RMS?b(f(b(normalized))*f(weight[i])):b(normalized*f(weight[i])+f(bias[i]));
  }
}
