// LAUNCH 144 128
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

extern "C" __attribute__((global,amdgpu_flat_work_group_size(128,128))) void attn_scores(ushort *out,const uint *q,const uint *cache,const float *mask) {
#pragma clang fp contract(off)
  uint lid=__ockl_get_local_id(0), lane=lid%32, L=lane%16, sub=lane/16;
  uint chunk=__ockl_get_group_id(0)*4+lid/32;            // over 8 kv heads x 2304/KPW chunks
  uint kvh=chunk/(2304/32), key0=(chunk%(2304/32))*32;
  // q words: 2 bf16 per word, head row = 64 words; lane L elements 4L..4L+3 -> words 2L,2L+1; L+16 -> 32+2L,33+2L
  uint qa[2][4];
  #pragma unroll
  for (uint h=0;h<2;h++) {
    const uint *qh=q+(kvh*2+h)*64;
    u2 a=*(const u2 *)(qh+2*L), b=*(const u2 *)(qh+32+2*L);
    qa[h][0]=a.x; qa[h][1]=a.y; qa[h][2]=b.x; qa[h][3]=b.y;
  }
  const uint *kbase=cache+(ulong)kvh*2304*64;
  for (uint p0=0;p0<16;p0+=4) {
    u2 ka[4],kb[4];
    #pragma unroll
    for (uint u=0;u<4;u++) {
      uint key=key0+(p0+u)*2+sub;
      ka[u]=*(const u2 *)(kbase+key*64+2*L); kb[u]=*(const u2 *)(kbase+key*64+32+2*L);
    }
    #pragma unroll
    for (uint u=0;u<4;u++) {
      uint key=key0+(p0+u)*2+sub;
      float res[2];
      #pragma unroll
      for (uint h=0;h<2;h++) {
        float pa=lo(qa[h][0])*lo(ka[u].x);
        pa=__builtin_fmaf(hi(qa[h][0]),hi(ka[u].x),pa);
        pa=__builtin_fmaf(lo(qa[h][1]),lo(ka[u].y),pa);
        pa=__builtin_fmaf(hi(qa[h][1]),hi(ka[u].y),pa);
        float pb=lo(qa[h][2])*lo(kb[u].x);
        pb=__builtin_fmaf(hi(qa[h][2]),hi(kb[u].x),pb);
        pb=__builtin_fmaf(lo(qa[h][3]),lo(kb[u].y),pb);
        pb=__builtin_fmaf(hi(qa[h][3]),hi(kb[u].y),pb);
        float v=pa+pb;                       // original swap-16 step
        v=v+swz(v,0x201f); v=v+swz(v,0x101f); v=v+swz(v,0x081f); v=v+swz(v,0x041f);
        res[h]=v;
      }
      if (L==0) {
        float m=mask[key];
        #pragma unroll
        for (uint h=0;h<2;h++) {
          float s=__builtin_bit_cast(float,rne(res[h]));
          s=__builtin_bit_cast(float,rne(s*__builtin_bit_cast(float,0x3db50000u)));
          out[(kvh*2+h)*2304+key]=(ushort)(rne(m+s)>>16);
        }
      }
    }
  }
}
