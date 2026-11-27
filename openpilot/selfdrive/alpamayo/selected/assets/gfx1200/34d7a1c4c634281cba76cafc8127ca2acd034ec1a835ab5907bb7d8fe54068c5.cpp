// LAUNCH 1 256
// Exact fusion of r_16_128 (RMS), r_16_128 (absmax of normed) and E_16_32_4 (FP8 quantize) for one 2048 BF16 row.
typedef unsigned uint; typedef unsigned short ushort; typedef unsigned char uchar;
typedef uint u4 __attribute__((ext_vector_type(4)));
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
#define SYNC() do { __builtin_amdgcn_fence(__ATOMIC_RELEASE,"workgroup"); __builtin_amdgcn_s_barrier(); __builtin_amdgcn_fence(__ATOMIC_ACQUIRE,"workgroup"); } while (0)
#define DEV __attribute__((device)) __attribute__((always_inline)) inline
DEV float bf(uint bits16) { return __builtin_bit_cast(float, bits16<<16); }
DEV float rne(float f) {
  uint b=__builtin_bit_cast(uint,f);
  uint nf=(b&0xffffu)?(b|0x10000u):b;
  uint r=((0u-b)&0x7f800000u)?(b+((b>>16)&1u)+0x7fffu):nf;
  return __builtin_bit_cast(float, r&0xffff0000u);
}
DEV float precise_sqrt(float x) {  // LLVM's correctly rounded f32 sqrt expansion on gfx12
  bool small = x < __builtin_bit_cast(float,0x0f800000u);
  float v = small ? x*__builtin_bit_cast(float,0x4f800000u) : x;
  float s = __builtin_amdgcn_sqrtf(v);
  float sm = __builtin_bit_cast(float,__builtin_bit_cast(uint,s)-1u), sp = __builtin_bit_cast(float,__builtin_bit_cast(uint,s)+1u);
  float rm = __builtin_fmaf(-sm, s, v), rp = __builtin_fmaf(-sp, s, v);
  float r = (0.0f >= rm) ? sm : s;
  r = (0.0f < rp) ? sp : r;
  r = small ? r*__builtin_bit_cast(float,0x37800000u) : r;
  return __builtin_isfpclass(v, 0x260) ? v : r;   // -0, +0, +inf
}
DEV uchar to_fp8(float v) {
  v = (v < -448.0f) ? -448.0f : v;
  v = (448.0f < v) ? 448.0f : v;
  if (__builtin_isfinite(v)) v = __builtin_amdgcn_fmed3f(v, 448.0f, -448.0f);
  return (uchar)(__builtin_amdgcn_cvt_pk_fp8_f32(v, v, 0, false) & 0xff);
}
extern "C" __attribute__((global,amdgpu_flat_work_group_size(256,256))) void prep_norm_fp8(uchar *q, float *scale_out, const u4 *x, const u4 *w) {
#pragma clang fp contract(off)
  __attribute__((shared,aligned(16))) u4 xs[256];
  __attribute__((shared,aligned(16))) float part[16];
  __attribute__((shared,aligned(16))) float red[8];
  __attribute__((shared,aligned(16))) float shared_rms, shared_scale;
  uint t = __ockl_get_local_id(0);
  u4 xv = x[t], wv = w[t];
  xs[t] = xv;
  SYNC();
  if (t < 16) {
    float acc = 0.0f;
    for (uint i = 0; i < 16; i++) {
      u4 v = xs[t*16+i];
      #pragma unroll
      for (uint j = 0; j < 4; j++) { float a = bf(v[j]&0xffffu), b = bf(v[j]>>16); acc = __builtin_fmaf(a, a, acc); acc = __builtin_fmaf(b, b, acc); }
    }
    part[t] = acc;
  }
  SYNC();
  if (t == 0) {
    float total = 0.0f + part[0];
    for (uint i = 1; i < 16; i++) total = total + part[i];
    shared_rms = precise_sqrt(__builtin_fmaf(total, __builtin_bit_cast(float,0x3a000000u), __builtin_bit_cast(float,0x3727c5acu)));
  }
  SYNC();
  float inv = __builtin_amdgcn_rcpf(shared_rms);
  float h[8]; float mx = -__builtin_inff();
  #pragma unroll
  for (uint j = 0; j < 4; j++) {
    float a = rne(bf(xv[j]&0xffffu)*inv), b = rne(bf(xv[j]>>16)*inv);
    h[2*j] = rne(bf(wv[j]&0xffffu)*a); h[2*j+1] = rne(bf(wv[j]>>16)*b);
  }
  #pragma unroll
  for (uint j = 0; j < 8; j++) { float s = (h[j] < 0.0f) ? -1.0f : 1.0f; s = (h[j] != 0.0f) ? s : 0.0f; float v = h[j]*s; mx = (mx < v) ? v : mx; }
  #pragma unroll
  for (uint d = 16; d > 0; d /= 2) { float o = __builtin_bit_cast(float,__builtin_amdgcn_ds_bpermute(4*((t%32)^d), __builtin_bit_cast(int,mx))); mx = (mx < o) ? o : mx; }
  if (t % 32 == 0) red[t/32] = mx;
  SYNC();
  if (t == 0) {
    float m = red[0];
    for (uint i = 1; i < 8; i++) m = (m < red[i]) ? red[i] : m;
    float s = m*__builtin_bit_cast(float,0x3b124925u);
    s = (s < __builtin_bit_cast(float,0x2b8cbcccu)) ? __builtin_bit_cast(float,0x2b8cbcccu) : s;
    shared_scale = s; scale_out[0] = s;
  }
  SYNC();
  float is = __builtin_amdgcn_rcpf(shared_scale);
  uint lo = 0, hi = 0;
  #pragma unroll
  for (uint j = 0; j < 4; j++) { lo |= (uint)to_fp8(h[j]*is) << (8*j); hi |= (uint)to_fp8(h[4+j]*is) << (8*j); }
  ((uint *)q)[2*t] = lo; ((uint *)q)[2*t+1] = hi;
}
