// LAUNCH 32 256
#define W 2048
#define U 4
#define DELTA 2
typedef unsigned uint; typedef unsigned char uchar; typedef unsigned short ushort; typedef unsigned long ulong;
typedef uint u4 __attribute__((ext_vector_type(4)));
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);
#define DEV __attribute__((device)) __attribute__((always_inline)) inline
#define SYNC() do { __builtin_amdgcn_fence(__ATOMIC_RELEASE,"workgroup"); __builtin_amdgcn_s_barrier(); __builtin_amdgcn_fence(__ATOMIC_ACQUIRE,"workgroup"); } while (0)
#define f8(word,byte) __builtin_amdgcn_cvt_f32_fp8((int)(word),byte)
DEV float shfl(float v, uint lane) { return __builtin_bit_cast(float,__builtin_amdgcn_ds_bpermute(4*lane,__builtin_bit_cast(uint,v))); }
DEV uint rne_bits(float f) {
  uint b=__builtin_bit_cast(uint,f);
  uint nf=(b&0xffffu)?(b|0x10000u):b;
  uint r=((0u-b)&0x7f800000u)?(b+((b>>16)&1u)+0x7fffu):nf;
  return r>>16;
}
DEV float bf(uint bits16) { return __builtin_bit_cast(float, bits16<<16); }
DEV float rnef(float f) { return bf(rne_bits(f)); }
extern "C" __attribute__((global,amdgpu_flat_work_group_size(256,256))) void qkv_rope_store(ushort *qout, ushort *cache, const uchar *x,
    const uchar *wq, const uchar *wk, const uchar *wv, const float *xs, const float *sq, const float *sk, const float *sv,
    const ushort *coss, const ushort *sins, const int *ctrl) {
#pragma clang fp contract(off)
  __attribute__((shared,aligned(16))) ushort hrow[128];
  uint lid=__ockl_get_local_id(0), lane=lid%32, wave=lid/32, rg=lane%4, h=(lane/4)%2, w8=lane/8;
  uint head=__ockl_get_group_id(0);
  const uchar *w; const float *ws; uint local;
  if (head<16u) { w=wq; ws=sq; local=head*8+wave; }
  else if (head<24u) { w=wk; ws=sk; local=(head-16)*8+wave; }
  else { w=wv; ws=sv; local=(head-24)*8+wave; }
  const uchar *wt=w+(ulong)local*(W/16)*256+h*64+rg*16;
  const uchar *xt=x+h*4;
  float acc[4]={0,0,0,0};
  for (uint k0=0;k0<W/64;k0+=U) {
    u4 A[U],B[U]; uint XA[U],XB[U];
    #pragma unroll
    for (uint u=0;u<U;u++) {
      uint t=(k0+u)*4+w8;
      A[u]=*(const u4 *)(wt+t*256); B[u]=*(const u4 *)(wt+t*256+128);
      XA[u]=*(const uint *)(xt+t*16); XB[u]=*(const uint *)(xt+t*16+8);
    }
    #pragma unroll
    for (uint u=0;u<U;u++) {
      float xv[8]={f8(XA[u],0),f8(XA[u],1),f8(XA[u],2),f8(XA[u],3),f8(XB[u],0),f8(XB[u],1),f8(XB[u],2),f8(XB[u],3)};
      #pragma unroll
      for (uint i=0;i<4;i++) {
        uint a=A[u][i], b=B[u][i];
        float s=xv[1]*f8(a,1);
        s=__builtin_fmaf(xv[0],f8(a,0),s);
        s=__builtin_fmaf(xv[2],f8(a,2),s);
        s=__builtin_fmaf(xv[3],f8(a,3),s);
        s=__builtin_fmaf(xv[4],f8(b,0),s);
        s=__builtin_fmaf(xv[5],f8(b,1),s);
        s=__builtin_fmaf(xv[6],f8(b,2),s);
        s=__builtin_fmaf(xv[7],f8(b,3),s);
        acc[i]=acc[i]+s;
      }
    }
  }
  float scale=xs[0]*ws[0];
  ushort res[4];
  #pragma unroll
  for (uint i=0;i<4;i++) {
    float q=acc[i]+shfl(acc[i],lane^4);
    float q1=shfl(q,(lane+8)%32), q2=shfl(q,(lane+16)%32), q3=shfl(q,(lane+24)%32);
    res[i]=(ushort)rne_bits((((q+q1)+q2)+q3)*scale);
  }
  if (lane<4) {
    #pragma unroll
    for (uint i=0;i<4;i++) hrow[wave*16+rg*4+i]=res[i];
  }
  SYNC();
  if (lid<128) {
    uint i=lid;
    float xi=bf(hrow[i]);
    ulong row=(ulong)(ctrl[0]+DELTA);
    if (head<24u) {
      float c=bf(coss[DELTA*128+i]), s=bf(sins[DELTA*128+i]);
      float rot=(i<64u)?rnef(-bf(hrow[i+64])):bf(hrow[i-64]);
      ushort r=(ushort)rne_bits(rnef(xi*c)+rnef(rot*s));
      if (head<16u) qout[head*128+i]=r;
      else cache[(((ulong)(head-16))*2304+row)*128+i]=r;
    } else {
      cache[(ulong)8*2304*128+(((ulong)(head-24))*2304+row)*128+i]=hrow[i];
    }
  }
}
