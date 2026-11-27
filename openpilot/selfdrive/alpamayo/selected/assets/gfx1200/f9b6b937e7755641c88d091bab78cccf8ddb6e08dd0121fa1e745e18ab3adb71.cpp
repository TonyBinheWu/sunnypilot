// LAUNCH 360 128
// Exact alpamayo_norm (WIDTH 1152, LayerNorm, eps 1e-6) with one wave per row. Lane l, slot w emulates thread
// t=w*32+l of the 256-thread original: same per-thread element order, same xor-16/8/4/2/1 lane tree, and the same
// sequential sum over the eight wave totals. The row is read once into registers. Optional per-row |out| maximum.
#define WIDTH 1152
#define ROWS 1440
#define ABSMAX 1
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
#define J 5  // elements per original thread: t, t+256, ..., t+1024 (the last only for t<128)
extern "C" __attribute__((global,amdgpu_flat_work_group_size(128,128)))
void alpamayo_norm_fast(u16 *out,const u16 *x,const u16 *weight,const u16 *bias
#if ABSMAX
,float *partial
#endif
) {
  int t=__ockl_get_local_id(0), lane=t%32, row=__ockl_get_group_id(0)*4+t/32;
  if(row>=ROWS) return;
  const u16 *xr=x+row*WIDTH;
  float v[8][J];
  #pragma unroll
  for(int w=0;w<8;w++) {
    #pragma unroll
    for(int j=0;j<J;j++) { int i=w*32+lane+256*j; v[w][j]=i<WIDTH?f(xr[i]):0.0f; }
  }
  float s[8];
  #pragma unroll
  for(int w=0;w<8;w++) {
    float a=0;
    #pragma unroll
    for(int j=0;j<J;j++) if(w*32+256*j<WIDTH) a+=v[w][j];
    s[w]=sum(a);
  }
  float mean=0;
  #pragma unroll
  for(int w=0;w<8;w++) mean+=s[w];
  mean/=WIDTH;
  #pragma unroll
  for(int w=0;w<8;w++) {
    float a=0;
    #pragma unroll
    for(int j=0;j<J;j++) if(w*32+256*j<WIDTH) { float d=v[w][j]-mean; a+=d*d; }
    s[w]=sum(a);
  }
  float variance=0;
  #pragma unroll
  for(int w=0;w<8;w++) variance+=s[w];
  variance/=WIDTH;
  float inv=__builtin_amdgcn_rsqf(variance+1.0000000000e-06f);
  float top=0.0f;
  #pragma unroll
  for(int w=0;w<8;w++) {
    #pragma unroll
    for(int j=0;j<J;j++) {
      int i=w*32+lane+256*j;
      if(w*32+256*j<WIDTH) {
        float normalized=(v[w][j]-mean)*inv;
        u16 o=b(normalized*f(weight[i])+f(bias[i]));
        out[row*WIDTH+i]=o;
        top=__builtin_fmaxf(top,__builtin_fabsf(f(o)));
      }
    }
  }
#if ABSMAX
  top=__builtin_fmaxf(top,shuffle<0x401f>(top)); top=__builtin_fmaxf(top,shuffle<0x201f>(top)); top=__builtin_fmaxf(top,shuffle<0x101f>(top));
  top=__builtin_fmaxf(top,shuffle<0x081f>(top)); top=__builtin_fmaxf(top,shuffle<0x041f>(top));
  if(lane==0) partial[row]=top;
#endif
}
