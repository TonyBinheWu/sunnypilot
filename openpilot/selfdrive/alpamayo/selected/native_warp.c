#include <stddef.h>
#include <stdint.h>

/* Match scipy.ndimage order=1, mode=nearest, including uint8 rounding.
 * Keep double multiplication order and disable floating-point contraction. */
void warp_u8(const uint8_t *restrict src, uint8_t *restrict dst, const int32_t *restrict offsets,
             const double *restrict fractions, size_t pixels, size_t source_pixels,
             size_t width, size_t height) {
  for (size_t i = 0; i < pixels; ++i) {
    size_t x = offsets[2*i], y = offsets[2*i+1];
    size_t p = y*width+x, q = p+(x+1 < width);
    size_t r = p+(y+1 < height ? width : 0), s = r+(x+1 < width);
    double dx = fractions[2*i], dy = fractions[2*i+1];
    for (size_t channel = 0; channel < 3; ++channel) {
      const uint8_t *in = src + channel * source_pixels;
      double value = 0.;
      value += (in[p] * (1.-dy)) * (1.-dx);
      value += (in[q] * (1.-dy)) * dx;
      value += (in[r] * dy) * (1.-dx);
      value += (in[s] * dy) * dx;
      dst[channel*pixels+i] = value > 255. ? 255 : value < 0. ? 0 : (uint8_t)(value+.5);
    }
  }
}

/* The same samples from interleaved HWC RGB, as the video decoder returns it. A planar copy of the full camera frame
 * cost about as much as the colour conversion itself. The arithmetic and the output are identical to warp_u8. */
#if defined(__aarch64__)
#include <arm_neon.h>

/* Exact u8 -> double conversion through an L1-resident table. */
#define U8_4(n) n, n+1., n+2., n+3.
#define U8_16(n) U8_4(n), U8_4(n+4.), U8_4(n+8.), U8_4(n+12.)
static const double U8_DOUBLE[256] = {
  U8_16(0.), U8_16(16.), U8_16(32.), U8_16(48.), U8_16(64.), U8_16(80.), U8_16(96.), U8_16(112.),
  U8_16(128.), U8_16(144.), U8_16(160.), U8_16(176.), U8_16(192.), U8_16(208.), U8_16(224.), U8_16(240.)};

static inline float64x2_t u8_pair(const uint8_t *src, size_t a, size_t b) {
  return vcombine_f64(vld1_f64(&U8_DOUBLE[src[a]]), vld1_f64(&U8_DOUBLE[src[b]]));
}
#endif

static inline uint8_t round_u8(double value) {
  return value > 255. ? 255 : value < 0. ? 0 : (uint8_t)(value+.5);
}

void warp_hwc_u8(const uint8_t *restrict src, uint8_t *restrict dst, const int32_t *restrict offsets,
                 const double *restrict fractions, size_t pixels, size_t width, size_t height) {
  size_t i = 0;
#if defined(__aarch64__)
  /* Two pixels per iteration in float64x2 lanes: the same IEEE operations in the same order as the scalar loop. */
  const float64x2_t one = vdupq_n_f64(1.), half = vdupq_n_f64(.5), top = vdupq_n_f64(255.);
  for (; i+1 < pixels; i += 2) {
    float64x2x2_t f = vld2q_f64(fractions+2*i);  /* val[0]: dx of both pixels, val[1]: dy */
    float64x2_t dx = f.val[0], dy = f.val[1];
    float64x2_t ndx = vsubq_f64(one, dx), ndy = vsubq_f64(one, dy);
    size_t p[2], q[2], r[2], t[2];
    for (int k = 0; k < 2; ++k) {
      size_t x = offsets[2*(i+k)], y = offsets[2*(i+k)+1];
      size_t pp = y*width+x, rr = pp+(y+1 < height ? width : 0), right = x+1 < width;
      p[k] = 3*pp; q[k] = 3*(pp+right); r[k] = 3*rr; t[k] = 3*(rr+right);
    }
    for (size_t channel = 0; channel < 3; ++channel) {
      float64x2_t value = vmulq_f64(vmulq_f64(u8_pair(src, p[0]+channel, p[1]+channel), ndy), ndx);
      value = vaddq_f64(value, vmulq_f64(vmulq_f64(u8_pair(src, q[0]+channel, q[1]+channel), ndy), dx));
      value = vaddq_f64(value, vmulq_f64(vmulq_f64(u8_pair(src, r[0]+channel, r[1]+channel), dy), ndx));
      value = vaddq_f64(value, vmulq_f64(vmulq_f64(u8_pair(src, t[0]+channel, t[1]+channel), dy), dx));
      /* Weights lie in [0, 1], so value >= 0: truncating min(value+.5, 255) equals round_u8(value). */
      uint64x2_t rounded = vcvtq_u64_f64(vminq_f64(vaddq_f64(value, half), top));
      dst[channel*pixels+i] = (uint8_t)vgetq_lane_u64(rounded, 0);
      dst[channel*pixels+i+1] = (uint8_t)vgetq_lane_u64(rounded, 1);
    }
  }
#endif
  for (; i < pixels; ++i) {
    size_t x = offsets[2*i], y = offsets[2*i+1];
    size_t p = y*width+x, q = p+(x+1 < width);
    size_t r = p+(y+1 < height ? width : 0), s = r+(x+1 < width);
    double dx = fractions[2*i], dy = fractions[2*i+1];
    for (size_t channel = 0; channel < 3; ++channel) {
      double value = 0.;
      value += (src[3*p+channel] * (1.-dy)) * (1.-dx);
      value += (src[3*q+channel] * (1.-dy)) * dx;
      value += (src[3*r+channel] * dy) * (1.-dx);
      value += (src[3*s+channel] * dy) * dx;
      dst[channel*pixels+i] = round_u8(value);
    }
  }
}
