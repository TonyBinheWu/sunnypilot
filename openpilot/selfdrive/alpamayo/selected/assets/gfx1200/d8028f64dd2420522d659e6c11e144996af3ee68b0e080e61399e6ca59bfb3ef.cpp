#define COUNT 829440
#define FINAL 0
#define INPUT unsigned short
#define CONVERT __builtin_bit_cast(float,(unsigned)x<<16)

#pragma clang fp contract(off)
#define DEV __attribute__((device)) __attribute__((always_inline)) inline
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);
DEV float value(INPUT x) { return CONVERT; }
template<int mask> DEV float shuffle(float x) {
  return __builtin_bit_cast(float,__builtin_amdgcn_ds_swizzle(__builtin_bit_cast(int,x),mask));
}
DEV float wave_max(float x) {
  x=__builtin_fmaxf(x,shuffle<0x401f>(x)); x=__builtin_fmaxf(x,shuffle<0x201f>(x));
  x=__builtin_fmaxf(x,shuffle<0x101f>(x)); x=__builtin_fmaxf(x,shuffle<0x081f>(x));
  return __builtin_fmaxf(x,shuffle<0x041f>(x));
}
extern "C" __attribute__((global,amdgpu_flat_work_group_size(256,256)))
void alpamayo_absmax(float *out, const INPUT *x) {
  int t=__ockl_get_local_id(0), output_group=__ockl_get_group_id(0);
  int chunks=(COUNT+4095)/4096;
  int image=FINAL?output_group:output_group/chunks, group=FINAL?0:output_group%chunks;
  __attribute__((shared,aligned(16))) float maxima[8];
  float maximum=0;
  int begin=FINAL?0:group*4096, end=FINAL?COUNT:(begin+4096<COUNT?begin+4096:COUNT);
  for(int i=begin+t;i<end;i+=256) maximum=__builtin_fmaxf(maximum,__builtin_fabsf(value(x[image*COUNT+i])));
  maximum=wave_max(maximum);
  if(t%32==0) maxima[t/32]=maximum;
  __builtin_amdgcn_fence(__ATOMIC_RELEASE,"workgroup"); __builtin_amdgcn_s_barrier();
  __builtin_amdgcn_fence(__ATOMIC_ACQUIRE,"workgroup");
  if(t==0) {
    maximum=0; for(int i=0;i<8;i++) maximum=__builtin_fmaxf(maximum,maxima[i]);
    out[output_group]=maximum;
  }
}
