// LAUNCH 32 128
#define W 2048
#define U 4
typedef unsigned uint; typedef unsigned char uchar; typedef unsigned short ushort;
typedef uint u4 __attribute__((ext_vector_type(4)));
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);
#define DEV __attribute__((device)) __attribute__((always_inline)) inline
#define f8(word,byte) __builtin_amdgcn_cvt_f32_fp8((int)(word),byte)
DEV float shfl(float v, uint lane) { return __builtin_bit_cast(float,__builtin_amdgcn_ds_bpermute(4*lane,__builtin_bit_cast(uint,v))); }
DEV ushort to_bf16(float f) {
  uint b=__builtin_bit_cast(uint,f);
  uint nf=(b&0xffffu)?(b|0x10000u):b;
  uint r=((0u-b)&0x7f800000u)?(b+((b>>16)&1u)+0x7fffu):nf;
  return (ushort)(r>>16);
}
extern "C" __attribute__((global,amdgpu_flat_work_group_size(128,128))) void fp8_gemv(ushort *out,const uchar *x,const uchar *w0,const float *xs,const float *s0) {
#pragma clang fp contract(off)
  uint lid=__ockl_get_local_id(0), lane=lid%32, rg=lane%4, h=(lane/4)%2, w8=lane/8;
  uint tile=__ockl_get_group_id(0)*4+lid/32;
  const uchar *w; const float *ws; uint local;
  if (tile<128u) { w=w0; ws=s0; local=tile-0u; }
  const uchar *wt=w+(unsigned long)local*(W/16)*256+h*64+rg*16;
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
    float q=acc[i]+shfl(acc[i],lane^4);          // halves h=0,1 (original lane, lane^16)
    float q1=shfl(q,(lane+8)%32), q2=shfl(q,(lane+16)%32), q3=shfl(q,(lane+24)%32);
    float total=((q+q1)+q2)+q3;                  // original LDS order over waves 0..3
    res[i]=to_bf16(total*scale);
  }
  if (lane<4) {
    uint row=tile*16+rg*4;
    *(uint *)(out+row)=uint(res[0])|(uint(res[1])<<16);
    *(uint *)(out+row+2)=uint(res[2])|(uint(res[3])<<16);
  }
}
