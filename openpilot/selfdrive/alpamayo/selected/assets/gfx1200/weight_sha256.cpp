// SHA-256 of (4096 destination bytes || 16 fresh challenge bytes), one leaf per lane.
// Rebuild with the pinned tinygrad.runtime.support.compiler_amd.compile_hip(source, "gfx1200").
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);

using u32 = unsigned int;
static_assert(sizeof(u32) == 4, "SHA-256 requires 32-bit words");
static __attribute__((device, always_inline)) inline u32 ror(u32 v, unsigned n) { return (v >> n) | (v << (32-n)); }

extern "C" __attribute__((global)) void weight_sha256(u32 *out, const u32 *data, const u32 *nonce) {
  const unsigned leaf = __ockl_get_group_id(0)*64 + __ockl_get_local_id(0);
  const u32 k[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2 };
  u32 h[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
  for (unsigned block=0; block<=64; ++block) {
    u32 w[16];
    #pragma unroll
    for (unsigned j=0; j<16; ++j) {
      if (block<64) w[j] = __builtin_bswap32(data[leaf*1024+block*16+j]);
      else if (j<4) w[j] = __builtin_bswap32(nonce[j]);
      else w[j] = j==4 ? 0x80000000U : j==15 ? (4096+16)*8 : 0;
    }
    u32 a=h[0], b=h[1], c=h[2], d=h[3], e=h[4], f=h[5], g=h[6], z=h[7];
    #pragma unroll
    for (unsigned i=0; i<64; ++i) {
      if (i>=16) {
        u32 x=w[(i-15)%16], y=w[(i-2)%16];
        w[i%16] += (ror(x,7)^ror(x,18)^(x>>3)) + w[(i-7)%16] + (ror(y,17)^ror(y,19)^(y>>10));
      }
      u32 t1=z+(ror(e,6)^ror(e,11)^ror(e,25))+((e&f)^(~e&g))+k[i]+w[i%16];
      u32 t2=(ror(a,2)^ror(a,13)^ror(a,22))+((a&b)^(a&c)^(b&c));
      z=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    h[0]+=a; h[1]+=b; h[2]+=c; h[3]+=d; h[4]+=e; h[5]+=f; h[6]+=g; h[7]+=z;
  }
  #pragma unroll
  for (unsigned i=0; i<8; ++i) out[leaf*8+i]=__builtin_bswap32(h[i]);
}
