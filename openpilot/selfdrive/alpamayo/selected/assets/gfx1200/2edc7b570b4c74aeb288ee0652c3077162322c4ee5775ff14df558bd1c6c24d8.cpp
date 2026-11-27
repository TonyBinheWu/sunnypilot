// LAUNCH 72 128
typedef unsigned uint; typedef unsigned short ushort; typedef unsigned long ulong;
typedef uint u2 __attribute__((ext_vector_type(2)));
typedef uint u4 __attribute__((ext_vector_type(4)));
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);
#define DEV __attribute__((device)) __attribute__((always_inline)) inline
DEV float lo(uint w) { return __builtin_bit_cast(float, w<<16); }
DEV float hi(uint w) { return __builtin_bit_cast(float, w&0xffff0000u); }
DEV uint rne(float f) {  // tinygrad float->bf16 bits (kept in the high half)
  uint b=__builtin_bit_cast(uint,f);
  uint nf=(b&0xffffu)?(b|0x10000u):b;
  uint r=((0u-b)&0x7f800000u)?(b+((b>>16)&1u)+0x7fffu):nf;
  return r&0xffff0000u;
}
#define swz(v,pattern) __builtin_bit_cast(float,__builtin_amdgcn_ds_swizzle(__builtin_bit_cast(int,(v)),(pattern)))

extern "C" __attribute__((global,amdgpu_flat_work_group_size(128,128))) void attn_values(float *out,const ushort *probs,const ushort *cache) {
#pragma clang fp contract(off)
  uint lid=__ockl_get_local_id(0), lane=lid%32;
  uint wv=__ockl_get_group_id(0)*4+lid/32;
  uint cg=wv%2, part=(wv/2)%18, kvh=wv/(2*18);
  uint col=cg*64+lane*2;
  const ushort *vb=cache+(ulong)8*2304*128+((ulong)kvh*2304+part*128)*128+col;
  const ushort *p0=probs+(kvh*2)*2304+part*128, *p1=p0+2304;
  float acc[2][2];
  #pragma unroll
  for (uint h=0;h<2;h++) for (uint c=0;c<2;c++) acc[h][c]=0;
  for (uint r0=0;r0<128;r0+=16) {
    uint vv[16]; u4 pa[16/8], pb[16/8];
    #pragma unroll
    for (uint u=0;u<16;u++) vv[u]=*(const uint *)(vb+(r0+u)*128);
    #pragma unroll
    for (uint u=0;u<16/8;u++) { pa[u]=*(const u4 *)(p0+r0+u*8); pb[u]=*(const u4 *)(p1+r0+u*8); }
    #pragma unroll
    for (uint u=0;u<16;u++) {
      uint wa=pa[u/8][(u%8)/2], wb=pb[u/8][(u%8)/2];
      float fa=(u%2)?hi(wa):lo(wa), fb=(u%2)?hi(wb):lo(wb);
      uint w=vv[u]; float v[2]={lo(w),hi(w)};
      #pragma unroll
      for (uint c=0;c<2;c++) { acc[0][c]=__builtin_fmaf(fa,v[c],acc[0][c]); acc[1][c]=__builtin_fmaf(fb,v[c],acc[1][c]); }
    }
  }
  #pragma unroll
  for (uint h=0;h<2;h++)
    #pragma unroll
    for (uint c=0;c<2;c++) out[((kvh*2+h)*18+part)*128+col+c]=acc[h][c];
}
