// LAUNCH 64 256 alpamayo_expert_attention scratch
// Fused diffusion-expert attention (one launch): BF16 scores, FP32 key mask, softmax and PV.
// Reads K/V directly from the plain KV cache plane (2,1,8,2304,128) and the 64 new action rows (1,8,64,128 each).
// Bit-identical to alpamayo_attention_scores_2x2(+mask) -> alpamayo_attention_softmax -> alpamayo_expert_pv_2x2 for
// inputs whose scores are not NaN or +-inf before masking.
// Workgroup: one head x 16 queries, 8 waves. Wave w owns key tiles 8i+w (i = 128-key chunk): columns 16w..16w+15 of
// each chunk, which are exactly the original softmax threads 16w..16w+15.
// The packed BF16 scores go to a global scratch (64 x 148 x 32 x 16 bytes, L2 resident) to keep VGPRs low.
#pragma clang fp contract(off)
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long size_t;
typedef short s8 __attribute__((ext_vector_type(8)));
typedef float f8 __attribute__((ext_vector_type(8)));
typedef float f4 __attribute__((ext_vector_type(4)));
typedef u32 u2v __attribute__((ext_vector_type(2)));
typedef u32 u4v __attribute__((ext_vector_type(4)));
#define DEV __attribute__((device)) __attribute__((always_inline)) inline
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);

#ifndef CH
#define CH 16      // key tiles per P chunk in LDS (multiple of 8), double buffered
#endif
#ifndef VD
#define VD 8       // V tiles in flight per wave
#endif
#ifndef SD
#define SD 4       // score tiles in flight per wave in the sum pass
#endif
#ifndef MINW
#define MINW 2     // workgroups per CU the register budget is set for
#endif
constexpr int Q=64, P=2304, KEYS=P+64, W=128, TILES=KEYS/16, CHUNKS=(KEYS+127)/128, NCH=(TILES+CH-1)/CH;
constexpr int LAST = TILES - 8*(CHUNKS - 1);  // waves that own a tile in the last 128-key chunk
static_assert(CH % 8 == 0, "chunk must hold whole tile columns");
constexpr float LOG2E = 1.4426950408889634f;

DEV u32 bits(float f) { return __builtin_bit_cast(u32, f); }
DEV float flt(u32 x) { return __builtin_bit_cast(float, x); }
// Round to nearest even BF16, kept in the high half. Equals tinygrad's cast_float_to_bf16 for every non-NaN input.
DEV u32 rne(float f) { u32 x = bits(f); return x + 0x7fffu + ((x >> 16) & 1u); }
DEV float rnef(float f) { return flt(rne(f) & 0xffff0000u); }
DEV u32 pack(u32 lo, u32 hi) { return __builtin_amdgcn_perm(hi, lo, 0x07060302u); }  // high halves of lo, hi
DEV f8 mma(s8 a, s8 b, f8 c) { return __builtin_amdgcn_wmma_f32_16x16x16_bf16_w32_gfx12(a, b, c); }
template <int pattern> DEV float swz(float x) { return flt(__builtin_amdgcn_ds_swizzle(bits(x), pattern)); }
DEV void sync() {
  __builtin_amdgcn_fence(__ATOMIC_RELEASE, "workgroup"); __builtin_amdgcn_s_barrier(); __builtin_amdgcn_fence(__ATOMIC_ACQUIRE, "workgroup");
}
#define FENCE() __builtin_amdgcn_sched_barrier(0)
// tinygrad RDNA4 WMMA layout: element j of lane half h holds logical k = j%4 + 4h + 8(j/4).
#define KSLOT(h, j) ((j)%4 + 4*(h) + 8*((j)/4))
DEV s8 frag(const u16 *base, int h) {
  u2v lo = *(const u2v *)(base + 4*h), hi = *(const u2v *)(base + 8 + 4*h);
  return __builtin_bit_cast(s8, (u4v){lo[0], lo[1], hi[0], hi[1]});
}
typedef __attribute__((address_space(1))) s8 gs8;
DEV s8 load_tr(const u16 *row) { return __builtin_amdgcn_global_load_tr_b128_v8i16((gs8 *)row); }
template <bool B> struct Flag { static constexpr bool value = B; };

// exp2 as lowered by LLVM for the softmax kernel: inputs below -126 are offset by 64 and the result scaled by 2^-64.
// The plain form is used only when no finite input of this wave is below -126; -inf gives 0 either way.
template <bool SLOW> DEV void exp8(float *x) {
#pragma unroll
  for (int j = 0; j < 8; j++) {
    if (SLOW) {
      const bool s = x[j] < -126.0f;
      x[j] = __builtin_amdgcn_ldexpf(__builtin_amdgcn_exp2f(x[j] + (s ? 64.0f : 0.0f)), s ? -64 : 0);
    } else {
      x[j] = __builtin_amdgcn_exp2f(x[j]);
    }
  }
}
DEV void unpack(u4v sc, float *x, float mx) {
#pragma unroll
  for (int k = 0; k < 4; k++) {
    x[2*k] = (flt(sc[k] << 16) - mx) * LOG2E;
    x[2*k + 1] = (flt(sc[k] & 0xffff0000u) - mx) * LOG2E;
  }
}

extern "C" __attribute__((global, amdgpu_flat_work_group_size(256, 256), amdgpu_waves_per_eu(4*MINW, 16)))
void alpamayo_expert_attention(u16 *out, const u16 *q, const u16 *knew, const u16 *vnew, const u16 *cache, const float *mask,
                               u4v *scratch
#if defined(DEBUG) || defined(TIMING)
  , u16 *dbg_scores, u16 *dbg_probs
#endif
) {
  const int thread = __ockl_get_local_id(0), lane = thread % 32, w = __builtin_amdgcn_readfirstlane(thread / 32), h = lane / 16, r = lane % 16;
  const int block = __ockl_get_group_id(0), head = block / 4, qb = block % 4, kh = head / 2;
#ifdef TIMING
#define TS(k) do { if (lane == 0) ((unsigned long *)dbg_scores)[(block*8 + w)*8 + (k)] = __builtin_amdgcn_s_sendmsg_rtnl(0x83); } while (0)
#else
#define TS(k) do {} while (0)
#endif
  TS(0);
  const u16 *kc = cache + (size_t)kh*P*W, *vc = cache + (size_t)(8 + kh)*P*W;
  const u16 *kn = knew + (size_t)kh*64*W, *vn = vnew + (size_t)kh*64*W;
  u4v *mine = scratch + (size_t)block*TILES*32 + lane;  // [tile][lane]

  __attribute__((shared)) float red[2][8][16];
  __attribute__((shared)) float total[16][4];
  __attribute__((shared)) float inverse[16];
  __attribute__((shared)) int general_mask;
  __attribute__((shared, aligned(16))) u4v qs[8][32];
  constexpr int PBYTES = 2*CH*512, REGION = PBYTES > 16*128*4 ? PBYTES : 16*128*4;
  __attribute__((shared, aligned(16))) char region[REGION];
  float (*parts)[128] = (float (*)[128])region;
  u4v *pbuf = (u4v *)region;  // [2][CH][32 lanes]

  // Q^T as the WMMA B operand (lane: query r, dims 16d + KSLOT(h, j)), staged once in LDS.
  if (w == 0) {
    const u16 *qrow = q + ((size_t)head*Q + qb*16 + r)*W;
#pragma unroll
    for (int d = 0; d < 8; d++) qs[d][lane] = __builtin_bit_cast(u4v, frag(qrow + d*16, h));
  }
  // Is every mask value +-0 or -inf? Then bf16(s + m) == s + m for the finite BF16 score s.
  {
    bool other = false;
    for (int k = thread; k < KEYS/4; k += 256) {
      const f4 m = ((const f4 *)mask)[k];
#pragma unroll
      for (int j = 0; j < 4; j++) other |= !(m[j] == 0.0f || m[j] == -__builtin_inff());
    }
    if (thread == 0) general_mask = 0;
    sync();
    if (__builtin_amdgcn_ballot_w32(other) && lane == 0) general_mask = 1;
    sync();
  }
  const bool general = __builtin_amdgcn_readfirstlane(general_mask);

  // Scores S^T = K Q^T. A row r holds key 16*tile + KSLOT(r/8, r%8), so C element (h, j) of lane (query r) holds
  // key 16*tile + KSLOT(h, j): the PV A-operand order. The WMMA k slots carry the original dims.
  const int krow_off = KSLOT(r/8, r%8);
  auto kbase = [&](int tile) { return tile < 144 ? kc + (size_t)tile*16*W : kn + (size_t)(tile - 144)*16*W; };
  float localmax = -__builtin_inff(), localmin = __builtin_inff();  // min: scores before masking (all finite)
  s8 ka[8], kb[8];
  auto kload = [&](s8 *kf, int tile) {
    const u16 *kx = kbase(tile) + krow_off*W;
#pragma unroll
    for (int d = 0; d < 8; d++) kf[d] = frag(kx + d*16, h);
  };
  const int ntiles = w < LAST ? CHUNKS : CHUNKS - 1;  // this wave's tiles: 8i + w, i < ntiles
  kload(ka, w);
  auto scores = [&](auto general_tag) {
    auto score_tile = [&](int i, s8 *kf, s8 *knext) {
      const int tile = 8*i + w;
      const float *mrow = mask + tile*16 + 4*h;
      const f4 m0 = *(const f4 *)mrow, m1 = *(const f4 *)(mrow + 8);
      kload(knext, i + 1 < ntiles ? tile + 8 : tile);  // the last tile reloads itself (unused)
      f8 c = {};
#pragma unroll
      for (int d = 0; d < 8; d++) c = mma(kf[d], __builtin_bit_cast(s8, qs[d][lane]), c);
      float s[8];
#pragma unroll
      for (int j = 0; j < 8; j++) {
        s[j] = rnef(rnef(c[j]) * flt(0x3DB50000u));  // BF16 score times bf16(128**-0.5)
        localmin = __builtin_fminf(localmin, s[j]);
        const float m = j < 4 ? m0[j] : m1[j - 4];
        s[j] = decltype(general_tag)::value ? rnef(s[j] + m) : s[j] + m;  // exact when m is +-0 or -inf
        localmax = __builtin_fmaxf(localmax, s[j]);  // order-free without NaN
#ifdef DEBUG
        dbg_scores[((size_t)head*Q + qb*16 + r)*KEYS + tile*16 + KSLOT(h, j)] = bits(s[j]) >> 16;
#endif
      }
      mine[tile*32] = (u4v){pack(bits(s[0]), bits(s[1])), pack(bits(s[2]), bits(s[3])),
                            pack(bits(s[4]), bits(s[5])), pack(bits(s[6]), bits(s[7]))};
    };
    // ntiles is 18 or 19: pairs, then the odd last tile.
#pragma unroll 1
    for (int i = 0; i + 1 < ntiles; i += 2) {
      score_tile(i, ka, kb);
      score_tile(i + 1, kb, ka);
    }
    if (ntiles % 2) score_tile(ntiles - 1, ka, kb);
  };
  if (general) scores(Flag<true>()); else scores(Flag<false>());
  TS(1);
  localmax = __builtin_fmaxf(localmax, swz<0x401f>(localmax));
  localmin = __builtin_fminf(localmin, swz<0x401f>(localmin));
  if (lane < 16) { red[0][w][lane] = localmax; red[1][w][lane] = localmin; }
  sync();
  float rowmax = red[0][0][r], rowmin = red[1][0][r];
#pragma unroll
  for (int k = 1; k < 8; k++) { rowmax = __builtin_fmaxf(rowmax, red[0][k][r]); rowmin = __builtin_fminf(rowmin, red[1][k][r]); }
  // Offset exp2 path needed only if some finite input is below -126; exp2 inputs are monotone in the score.
  const bool slow = general || (rowmin - rowmax) * LOG2E < -126.0f;
  const bool wslow = __builtin_amdgcn_ballot_w32(slow) != 0;

  // Per original softmax thread (column 16w + KSLOT(h, j) of each chunk): one sequential FP32 sum over the chunks.
  // The scratch stores of this wave are visible to its own loads (same wave, program order).
  float acc[8];
  auto sums = [&](auto slow_tag) {
    auto step = [&](int i, u4v sv) {
      float x[8];
      unpack(sv, x, rowmax);
      exp8<decltype(slow_tag)::value>(x);
#pragma unroll
      for (int j = 0; j < 8; j++) acc[j] = i == 0 ? x[j] : acc[j] + x[j];
    };
    // Tiles of this wave: 8i + w. Load two ahead.
    u4v a0 = mine[w*32], a1 = mine[(8 + w)*32];
    {
      float x[8];
      unpack(a0, x, rowmax);
      exp8<decltype(slow_tag)::value>(x);
#pragma unroll
      for (int j = 0; j < 8; j++) acc[j] = x[j];
    }
    int i = 1;
#pragma unroll 1
    for (; i + 1 < ntiles; i += 2) {
      u4v b0 = mine[(8*(i + 1) + w)*32];
      step(i, a1);
      u4v b1 = mine[(8*(i + 2 < ntiles ? i + 2 : i + 1) + w)*32];
      step(i + 1, b0);
      a1 = b1;
    }
    if (i < ntiles) step(i, a1);
  };
  if (wslow) sums(Flag<true>()); else sums(Flag<false>());
#pragma unroll
  for (int j = 0; j < 8; j++) parts[r][16*w + KSLOT(h, j)] = acc[j];
  sync();
  // Original tree: each softmax wave reduces its 32 threads with ds_swizzle XOR 16, 8, 4, 2, 1.
  {
    float x[8];
#pragma unroll
    for (int k = 0; k < 8; k++) x[k] = parts[(w*8 + k) / 4][32*((w*8 + k) % 4) + lane];
#pragma unroll
    for (int k = 0; k < 8; k++) x[k] = x[k] + swz<0x401f>(x[k]);
#pragma unroll
    for (int k = 0; k < 8; k++) x[k] = x[k] + swz<0x201f>(x[k]);
#pragma unroll
    for (int k = 0; k < 8; k++) x[k] = x[k] + swz<0x101f>(x[k]);
#pragma unroll
    for (int k = 0; k < 8; k++) x[k] = x[k] + swz<0x081f>(x[k]);
#pragma unroll
    for (int k = 0; k < 8; k++) x[k] = x[k] + swz<0x041f>(x[k]);
    if (lane == 0) {
#pragma unroll
      for (int k = 0; k < 8; k++) total[(w*8 + k) / 4][(w*8 + k) % 4] = x[k];
    }
  }
  sync();
  if (thread < 16) inverse[thread] = __builtin_amdgcn_rcpf(((total[thread][0] + total[thread][1]) + total[thread][2]) + total[thread][3]);
  sync();
  const float inv = inverse[r];
  TS(2);

  // PV: wave w computes dims 16w..16w+15 of the 16 queries; one FP32 WMMA chain over all key tiles in order.
  // P = bf16(e * inv) is produced chunk by chunk from the scratch scores into a double-buffered LDS chunk.
  const int vkey = KSLOT(h, lane % 8), vcol = 16*w + (lane / 8) % 2 * 8;
  auto vload = [&](int tile) {
    return load_tr((tile < 144 ? vc + (size_t)tile*16*W : vn + (size_t)(tile - 144)*16*W) + vkey*W + vcol);
  };
  s8 v[VD];
#pragma unroll
  for (int u = 0; u < VD; u++) v[u] = vload(u);
  auto pv = [&](auto slow_tag) {
    auto put = [&](int c) {  // this wave's P tiles of chunk c into buffer c%2
      u4v sv[CH/8];
#pragma unroll
      for (int k = 0; k < CH/8; k++) {
        const int i = c*(CH/8) + k;
        sv[k] = mine[(8*(i < ntiles ? i : 0) + w)*32];
      }
#pragma unroll
      for (int k = 0; k < CH/8; k++) {
        const int i = c*(CH/8) + k;
        if (i < ntiles) {
          float x[8];
          unpack(sv[k], x, rowmax);
          exp8<decltype(slow_tag)::value>(x);
          u4v p;
#pragma unroll
          for (int j = 0; j < 4; j++) p[j] = pack(rne(x[2*j] * inv), rne(x[2*j + 1] * inv));
#ifdef DEBUG
#pragma unroll
          for (int j = 0; j < 4; j++) {
            dbg_probs[((size_t)head*Q + qb*16 + r)*KEYS + (8*i + w)*16 + KSLOT(h, 2*j)] = p[j] & 0xffffu;
            dbg_probs[((size_t)head*Q + qb*16 + r)*KEYS + (8*i + w)*16 + KSLOT(h, 2*j + 1)] = p[j] >> 16;
          }
#endif
          pbuf[((c % 2)*CH + 8*k + w)*32 + lane] = p;
        }
      }
    };
    sync();  // softmax scratch (parts) consumed
    put(0);
    f8 o = {};
    auto chunk = [&](int c, bool more, int count) {
      sync();
      if (more) put(c + 1);
      const u4v *pb = pbuf + (c % 2)*CH*32 + lane;
      u4v pcur = pb[0];
#pragma unroll
      for (int u = 0; u < CH; u++) {
        if (u < count) {
          u4v pnext = pcur;
          if (u + 1 < count) pnext = pb[(u + 1)*32];
          o = mma(__builtin_bit_cast(s8, pcur), v[u % VD], o);
          const int tile = c*CH + u;
          v[u % VD] = vload(tile + VD < TILES ? tile + VD : TILES - 1);  // tail reloads are unused
          pcur = pnext;
        }
      }
    };
    static_assert(CH % VD == 0, "V ring must align with chunks");
#pragma unroll 1
    for (int c = 0; c < NCH - 1; c++) chunk(c, true, CH);
    chunk(NCH - 1, false, TILES - (NCH - 1)*CH);
    TS(3);
#pragma unroll
    for (int j = 0; j < 8; j++) out[((size_t)head*Q + qb*16 + 8*h + j)*W + 16*w + r] = rne(o[j]) >> 16;
  };
  if (wslow) pv(Flag<true>()); else pv(Flag<false>());
}
