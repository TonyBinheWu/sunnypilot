#define WIDTH 2048
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
// tinygrad (x.float()/scale).clamp(-448,448): fdiv afn lowers to a hardware reciprocal and one rounded multiply.
DEV float quantized(float x,float inverse_scale) {
  float v=x*inverse_scale;
  v=v<-448.0f?-448.0f:v;
  return 448.0f<v?448.0f:v;
}
// RMS norm (identical arithmetic and reduction order to alpamayo_norm), then fixed-scale FP8 written in amd_gemm.pack layout.
extern "C" __attribute__((global,amdgpu_flat_work_group_size(256,256)))
void alpamayo_norm_fp8(unsigned *out,const u16 *x,const u16 *weight,const float *scale) {
  int t=__ockl_get_local_id(0), row=__ockl_get_group_id(0), wave=t/32, lane=t%32;
  __attribute__((shared,aligned(16))) float sums[8];
  float squared=0;
  for(int i=t;i<WIDTH;i+=256) { float v=f(x[row*WIDTH+i])-0.0f; squared+=v*v; }
  squared=sum(squared); if(lane==0) sums[wave]=squared; barrier();
  float variance=0; for(int i=0;i<8;i++) variance+=sums[i]; variance/=WIDTH;
  float inv=__builtin_amdgcn_rsqf(variance+EPSILON);
  float inverse_scale=__builtin_amdgcn_rcpf(scale[0]);
  #pragma unroll
  for(int chunk=0;chunk<WIDTH/1024;chunk++) {
    int c=chunk*1024+t*4;
    float q[4];
    #pragma unroll
    for(int j=0;j<4;j++) {
      float normalized=(f(x[row*WIDTH+c+j])-0.0f)*inv;
      q[j]=quantized(f(b(f(b(normalized))*f(weight[c+j]))),inverse_scale);
    }
    unsigned low=__builtin_amdgcn_cvt_pk_fp8_f32(q[0],q[1],0,false);
    unsigned word=__builtin_amdgcn_cvt_pk_fp8_f32(q[2],q[3],low,true);
    // Packed byte (row/16*(W/16)+c/16)*256+(c%16/4)*64+(row%16)*4+c%4, with c%4==0.
    out[((row/16)*(WIDTH/16)+c/16)*64+(c%16/4)*16+row%16]=word;
  }
}
