/* 768x432 CHW bytes -> 576x320 antialiased bicubic -> 720 checkpoint patches. */
#include <arm_neon.h>
#include <fenv.h>
#include <math.h>
#include <pthread.h>
#include <stddef.h>
#include <stdint.h>

#if __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error little-endian pixel groups required
#endif
#include "tables.h"

typedef float32x4_t V;
typedef uint8x16_t B;
#define load(p) vld1q_f32(p)
#define splat(a) vdupq_n_f32(a)
#define fused(u, w, a) vfmaq_f32(a, u, w)
#define shift(a, b, i) vextq_f32(a, b, i)

/* Four lanes process independent groups of four source pixels in the same CHW row. */
static inline void channels(const uint8_t *src, V *p) {
  uint32x4_t v = vreinterpretq_u32_u8(vld1q_u8(src)), m = vdupq_n_u32(255);
  p[0] = vcvtq_f32_u32(vandq_u32(v, m));
  p[1] = vcvtq_f32_u32(vandq_u32(vshrq_n_u32(v, 8), m));
  p[2] = vcvtq_f32_u32(vandq_u32(vshrq_n_u32(v, 16), m));
  p[3] = vcvtq_f32_u32(vshrq_n_u32(v, 24));
}

static inline void store3f(float *dst, V a, V b, V c) {
  float32x4x3_t v = {{a, b, c}};
  vst3q_f32(dst, v);
}

/* Round to nearest even, then saturate to a byte. */
static inline B byte16(V a, V b, V c, V d) {
  uint16x8_t ab = vcombine_u16(vqmovun_s32(vcvtnq_s32_f32(a)), vqmovun_s32(vcvtnq_s32_f32(b)));
  uint16x8_t cd = vcombine_u16(vqmovun_s32(vcvtnq_s32_f32(c)), vqmovun_s32(vcvtnq_s32_f32(d)));
  return vcombine_u8(vqmovn_u16(ab), vqmovn_u16(cd));
}

static inline void store3b(uint8_t *dst, B a, B b, B c) {
  uint8x16x3_t v = {{a, b, c}};
  vst3q_u8(dst, v);
}

/* ARM Torch starts with a binary32 product, then fuses each remaining tap in source order. */
#define F5(s0, s1, s2, s3, s4, k) \
  fused(s4, load(k[4]), fused(s3, load(k[3]), fused(s2, load(k[2]), fused(s1, load(k[1]), s0 * load(k[0])))))

static inline void edge(float *out, const uint8_t *src, int from, int to) {
  for (int x = from; x < to; x++) {
    const uint8_t *p = src + xi[x];
    const float *w = xw[x];
    float t = p[0] * w[0];
    for (int j = 1; j < xn[x]; j++) t = fmaf(p[j], w[j], t);
    out[x] = t;
  }
}

static inline void horizontal(float *out, const uint8_t *src) {
  edge(out, src, 0, 12);
  V prev[4], cur[4], next[4];
  channels(src, prev);
  channels(src + 16, cur);
  for (int b = 1; b < 47; b++) {
    channels(src + 16 * (b + 1), next);
    V m2 = shift(prev[2], cur[2], 3), m1 = shift(prev[3], cur[3], 3);
    V p4 = shift(cur[0], next[0], 1), p5 = shift(cur[1], next[1], 1);
    const float (*k)[4] = phase[b];
    V a = F5(m2, m1, cur[0], cur[1], cur[2], k);
    k += 5;
    V v = fused(p4, load(k[5]), F5(m1, cur[0], cur[1], cur[2], cur[3], k));
    k += 6;
    V c = F5(cur[1], cur[2], cur[3], p4, p5, k);
    store3f(out + 12*b, a, v, c);
    for (int i = 0; i < 4; i++) { prev[i] = cur[i]; cur[i] = next[i]; }
  }
  edge(out, src, 564, 576);
}

static inline V vertical(float *const *r, const float *w, int x, int n) {
  V a = load(r[0] + x) * splat(w[0]);
  if (n == 3) return fused(load(r[2] + x), splat(w[2]), fused(load(r[1] + x), splat(w[1]), a));
  a = fused(load(r[1] + x), splat(w[1]), a);
  a = fused(load(r[2] + x), splat(w[2]), a);
  a = fused(load(r[3] + x), splat(w[3]), a);
  a = fused(load(r[4] + x), splat(w[4]), a);
  return n == 5 ? a : fused(load(r[5] + x), splat(w[5]), a);
}

typedef struct { const uint8_t *in; uint8_t *out; int begin, end; } Job;

static void *band(void *arg) {
  Job j = *(Job *)arg;
  _Alignas(64) float ring[8][3][576];
  int nextrow = yi[j.begin];
  for (int y = j.begin; y < j.end; y++) {
    int lo = yi[y], n = yn[y];
    const float *w = yw[y];
    while (nextrow < lo + n) {
      for (int c = 0; c < 3; c++) horizontal(ring[nextrow & 7][c], j.in + (c*432 + nextrow)*768);
      nextrow++;
    }
    float *rp[3][6];
    for (int c = 0; c < 3; c++)
      for (int t = 0; t < n; t++) rp[c][t] = ring[(lo+t) & 7][c];
    for (int x = 0; x < 576; x += 16) {
      B rgb[3];
      for (int c = 0; c < 3; c++) {
        float **r = rp[c];
        rgb[c] = byte16(vertical(r, w, x, n), vertical(r, w, x+4, n), vertical(r, w, x+8, n), vertical(r, w, x+12, n));
      }
      /* Block-major 2x2 patches; each 16x16 patch contains interleaved RGB bytes. */
      int patch = ((y/32*18 + x/32)*2 + (y/16%2))*2 + x/16%2;
      store3b(j.out + patch*768 + (y%16)*48, rgb[0], rgb[1], rgb[2]);
    }
  }
  return NULL;
}

/* Borrow nonoverlapping buffers until both row bands finish. */
int fresh_patch(const uint8_t *in, size_t ni, uint8_t *out, size_t no, int workers) {
  if (!in || !out || ni != 995328 || no != 552960 || (workers != 1 && workers != 2) || fegetround() != FE_TONEAREST) return 1;
  uintptr_t a = (uintptr_t)in, b = (uintptr_t)out;
  if (a <= b ? b-a < ni : a-b < no) return 1;
  Job first = {in, out, 0, workers == 2 ? 160 : 320};
  if (workers == 1) { band(&first); return 0; }
  Job second = {in, out, 160, 320};
  pthread_t t;
  if (pthread_create(&t, NULL, band, &second)) return 2;
  band(&first);
  return pthread_join(t, NULL) ? 3 : 0;
}
