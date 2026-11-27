#define N 2048
#define K 9216
// Compiled separately for N=9216/K=2048 and N=2048/K=9216.
#define DEV __attribute__((device)) __attribute__((always_inline)) inline
#define GLOBAL __attribute__((global,amdgpu_flat_work_group_size(128,128)))
typedef unsigned uint;
typedef unsigned short ushort;
typedef _Float16 h2 __attribute__((ext_vector_type(2)));
typedef _Float16 h8 __attribute__((ext_vector_type(8)));
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);

#ifdef PACK
// Decode finite OCP E4M3 (exponent 15, mantissa <=6 is finite; max=448).
DEV float e4m3(uint b) {
  uint a=b&127u, e=a>>3, m=a&7u;
  float v=e?__builtin_bit_cast(float,((e+120u)<<23)|(m<<20)):float(m)*(1.f/512.f);
  return (b&128u)?-v:v;
}
extern "C" GLOBAL void projection_w4_pack(uint *out,const uint *in) {
  uint i=__ockl_get_group_id(0)*128+__ockl_get_local_id(0);
  uint row=(i/(K/64*16))*16+i%16, start=((i/16)%(K/64))*64;
  ushort h[2];
  #pragma unroll
  for (uint g=0;g<2;g++) {
    float w[32]; float mx=0;
    #pragma unroll
    for(uint j=0;j<8;j++) {
      uint k=start+g*32+j*4;
      uint v=in[((row/16)*(K/16)+k/16)*64+((k%16)/4)*16+row%16];
      #pragma unroll
      for(uint t=0;t<4;t++) { w[4*j+t]=e4m3((v>>(8*t))&255); mx=__builtin_fmaxf(mx,__builtin_fabsf(w[4*j+t])); }
    }
    _Float16 s=(_Float16)(mx==0?1.f:mx/7.f);
    h[g]=__builtin_bit_cast(ushort,s);
    #pragma unroll
    for(uint j=0;j<4;j++) {
      uint word=0;
      #pragma unroll
      for(uint t=0;t<8;t++) {
        int q=(int)__builtin_rintf(w[8*j+t]/float(s));
        uint nib=uint((q>7?7:q< -7?-7:q)+8);
        word|=nib<<(4*(t/2)+(t%2)*16);
      }
      out[row*(K/8)+start/8+g*4+j]=word;
    }
  }
  out[N*(K/8)+row*(K/64)+start/64]=uint(h[0])|(uint(h[1])<<16);
}
#else
DEV h2 deq2(uint w) {
  const h2 shift={1032,1032};
  return __builtin_bit_cast(h2,(w&0x000f000fu)|0x64006400u)-shift;
}
extern "C" GLOBAL void projection_w4_gemv(ushort *out,const h8 *xs,const uint *weights,const float *asc,const float *wsc) {
  uint lid=__ockl_get_local_id(0),lane=lid%32,row=__ockl_get_group_id(0)*4+lid/32;
  const _Float16 *sc=(const _Float16 *)(weights+N*(K/8))+row*(K/32);
  float acc=0;
  #pragma clang loop unroll_count(2)
  for (uint j=lane;j<K/8;j+=32) {
    h8 x=xs[j]; uint word=weights[row*(K/8)+j];
    float v=0;
    #pragma unroll
    for (uint p=0;p<4;p++) {
      h2 a={x[2*p],x[2*p+1]};
      v=__builtin_amdgcn_fdot2(a,deq2(word>>(p*4)),v,false);
    }
    acc=__builtin_fmaf(v,float(sc[j/4]),acc);
  }
  #pragma unroll
  for (uint d=16;d>0;d/=2)
    acc+=__builtin_bit_cast(float,__builtin_amdgcn_ds_bpermute(4*(lane^d),__builtin_bit_cast(uint,acc)));
  if (!lane) {
    uint b=__builtin_bit_cast(uint,acc*(asc[0]*wsc[0]));
    out[row]=(b+0x7fff+((b>>16)&1))>>16;
  }
}
#endif
