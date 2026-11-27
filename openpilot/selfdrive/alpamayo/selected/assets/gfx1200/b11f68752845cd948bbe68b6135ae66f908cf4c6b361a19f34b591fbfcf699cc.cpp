// LAUNCH 1 384
// prepD: exact fusion of alpamayo_serial_fc2_scale, E_96_32_3 (ReLU^2 FP8 quantize) and E_96_32_3 (FP8 -> FP16).
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

typedef unsigned short us4 __attribute__((ext_vector_type(4)));
DEV ushort fp8_to_f16(uchar b) { _Float16 h = (_Float16)__builtin_amdgcn_cvt_f32_fp8((int)b, 0); return __builtin_bit_cast(ushort, h); }
extern "C" __attribute__((global,amdgpu_flat_work_group_size(384,384))) void prep_relu2_f16(ushort *q, float *scale_out, const u4 *raw) {
#pragma clang fp contract(off)
  __attribute__((shared,aligned(16))) uint red[12];
  __attribute__((shared,aligned(16))) float shared_scale;
  uint t = __ockl_get_local_id(0);
  u4 v[3]; uint peak = 0;
  #pragma unroll
  for (uint i = 0; i < 3; i++) {
    v[i] = raw[i*384+t];
    #pragma unroll
    for (uint j = 0; j < 4; j++) {
      uint a = v[i][j]&0xffffu, b = v[i][j]>>16;
      peak = __builtin_elementwise_max(peak, a <= 0x7f80u ? a : 0u); peak = __builtin_elementwise_max(peak, b <= 0x7f80u ? b : 0u);
    }
  }
  #pragma unroll
  for (uint d = 16; d > 0; d /= 2) peak = __builtin_elementwise_max(peak, (uint)__builtin_amdgcn_ds_bpermute(4*((t%32)^d), (int)peak));
  if (t % 32 == 0) red[t/32] = peak;
  SYNC();
  if (t == 0) {
    uint m = red[0];
    for (uint i = 1; i < 12; i++) m = __builtin_elementwise_max(m, red[i]);
    float value = __builtin_bit_cast(float, m<<16);
    float s = rne(value*value)*__builtin_bit_cast(float,0x3b124925u);
    s = (s < __builtin_bit_cast(float,0x2b8cbcccu)) ? __builtin_bit_cast(float,0x2b8cbcccu) : s;
    shared_scale = s; scale_out[0] = s;
  }
  SYNC();
  float is = __builtin_amdgcn_rcpf(shared_scale);
  #pragma unroll
  for (uint i = 0; i < 3; i++) {
    us4 a, b;
    #pragma unroll
    for (uint j = 0; j < 4; j++) {
      float x0 = bf(v[i][j]&0xffffu), x1 = bf(v[i][j]>>16);
      float r0 = (0.0f < x0) ? x0 : 0.0f, r1 = (0.0f < x1) ? x1 : 0.0f;
      ushort f0 = fp8_to_f16(to_fp8(rne(r0*r0)*is)), f1 = fp8_to_f16(to_fp8(rne(r1*r1)*is));
      if (j < 2) { a[2*j] = f0; a[2*j+1] = f1; } else { b[2*(j-2)] = f0; b[2*(j-2)+1] = f1; }
    }
    ((us4 *)q)[2*(i*384+t)] = a; ((us4 *)q)[2*(i*384+t)+1] = b;
  }
}
