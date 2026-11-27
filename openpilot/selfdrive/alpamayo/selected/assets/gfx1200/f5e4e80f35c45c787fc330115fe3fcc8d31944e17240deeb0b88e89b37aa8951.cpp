// LAUNCH 360 32
#define M 1440
#define N 1152
#define K 4304
#define TM 3
#define TN 6
#define WM 1
#define WN 1
#define ACC 1
#define RESIDUAL 1
#define GELUMAX 0
#define PF 3
#define SWAP 1
#define GOUT 0
#define PMAX 0
#define ROWS_PER_IMAGE 720
#define MB (M/16)
#define NB ((N+15)/16)
#define MT ((MB+TM-1)/TM)
#define NT ((NB+TN-1)/TN)
#define GM ((MT+WM-1)/WM)
#define GN ((NT+WN-1)/WN)

#pragma clang fp contract(off)
#define DEV __attribute__((device,always_inline)) inline
typedef int i2 __attribute__((ext_vector_type(2)));
typedef float f8 __attribute__((ext_vector_type(8)));
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);
// Exact pinned tinygrad BF16 cast.
DEV unsigned short bf(float value) {
  unsigned b=__builtin_bit_cast(unsigned,value);
  unsigned regular=b+((b>>16)&1)+0x7fffu;
  unsigned special=b|(((b&0xffffu)!=0)<<16);
  unsigned mask=0u-(((-b & 0x7f800000u)!=0));
  asm("" : "+v"(mask));
  return (unsigned short)(((regular&mask)|(special&~mask))>>16);
}
DEV float frombf(unsigned short value) { return __builtin_bit_cast(float,((unsigned)value)<<16); }
// tinygrad gelu(approximate='tanh') on a BF16 input, as lowered by AMD LLVM (FMA, exp2 range scaling, rcp*mul).
DEV float gelu(float x) {
  float x3=(x*x)*x;
  float t=__builtin_fmaf(x3,__builtin_bit_cast(float,0x3d372713u),x);
  float y=t*__builtin_bit_cast(float,0xc0135761u);
  bool small=y<-126.0f;
  float e=__builtin_amdgcn_exp2f(small?y+64.0f:y);
  e=__builtin_amdgcn_ldexpf(e,small?-64:0);
  return x*__builtin_amdgcn_rcpf(1.0f+e);
}
#if SWAP
// Transposed product: lane%16 is the output row and the eight values are consecutive columns.
#define WMMA(a,b,c) __builtin_amdgcn_wmma_f32_16x16x16_fp8_fp8_w32_gfx12(b,a,c)
#else
#define WMMA(a,b,c) __builtin_amdgcn_wmma_f32_16x16x16_fp8_fp8_w32_gfx12(a,b,c)
#endif
typedef unsigned u4 __attribute__((ext_vector_type(4)));
DEV i2 fragment(const unsigned *ptr,unsigned offset) { return (i2){(int)ptr[offset],(int)ptr[offset+32]}; }
extern "C" __attribute__((global,amdgpu_flat_work_group_size(32*WM*WN,32*WM*WN)))
void fc2_k(unsigned short *__restrict out,const unsigned *__restrict x,const unsigned *__restrict weight,
            const float *__restrict xs,const float *__restrict ws,const unsigned short *__restrict bias
#if RESIDUAL
            ,const unsigned short *__restrict res
#endif
#if GELUMAX
            ,unsigned *__restrict gmax
#endif
#if PMAX
            ,unsigned *__restrict partial
#endif
            ) {
  unsigned thread=__ockl_get_local_id(0),lane=thread%32,wave=thread/32;
  unsigned g=__ockl_get_group_id(0);
  // Row groups fastest: neighbouring workgroups share weight tiles.
  unsigned gm=g%GM,gn=g/GM;
  unsigned mt=gm*WM+wave%WM,nt=gn*WN+wave/WM;
  if(mt>=MT || nt>=NT) return;
  f8 accum[TM][TN];
  #pragma unroll
  for(unsigned i=0;i<TM;i++) {
    #pragma unroll
    for(unsigned j=0;j<TN;j++) accum[i][j]=(f8){0};
  }
  // Edge tiles shift inside the matrix: overlapping waves write identical values. Fragment offsets stay constant strides.
  unsigned mb0=mt*TM<MB-TM?mt*TM:MB-TM,nb0=nt*TN<NB-TN?nt*TN:NB-TN;
  const unsigned *pa=x+mb0*(K/16)*64+lane,*pb=weight+nb0*(K/16)*64+lane;
  const f8 zero=(f8){0};
#define S ((K/16)*64)
#define KS (K/16)
#if ACC
#define COMPUTE(A,B) { _Pragma("unroll") for(unsigned i=0;i<TM;i++) { _Pragma("unroll") for(unsigned j=0;j<TN;j++) accum[i][j]=WMMA(A[i],B[j],accum[i][j]); } }
#else
#define COMPUTE(A,B) { f8 tmp[TM][TN]; \
    _Pragma("unroll") for(unsigned i=0;i<TM;i++) { _Pragma("unroll") for(unsigned j=0;j<TN;j++) tmp[i][j]=WMMA(A[i],B[j],zero); } \
    _Pragma("unroll") for(unsigned i=0;i<TM;i++) { _Pragma("unroll") for(unsigned j=0;j<TN;j++) accum[i][j]=accum[i][j]+tmp[i][j]; } }
#endif
#define LOAD(A,B,kk) { _Pragma("unroll") for(unsigned i=0;i<TM;i++) A[i]=fragment(pa,i*S+(kk)*64); \
    _Pragma("unroll") for(unsigned j=0;j<TN;j++) B[j]=fragment(pb,j*S+(kk)*64); }
#if PF
  // Register ring of PF fragment sets: loads run PF k-steps ahead. Each accumulator still adds k in ascending order.
  i2 a[PF][TM],b[PF][TN];
  #pragma unroll
  for(unsigned s=0;s<PF;s++) LOAD(a[s],b[s],s<KS?s:0)
  for(unsigned k0=0;k0<KS;k0+=PF) {
    #pragma unroll
    for(unsigned s=0;s<PF;s++) {
      unsigned k=k0+s;
      if(k<KS) {
        COMPUTE(a[s],b[s])
        unsigned nk=k+PF<KS?k+PF:k;
        LOAD(a[s],b[s],nk)
      }
    }
  }
#else
  #pragma clang loop unroll_count(1)
  for(unsigned k=0;k<KS;k++) {
    i2 a[TM],b[TN];
    LOAD(a,b,k)
    COMPUTE(a,b)
  }
#endif
  float wscale=ws[0];
#if SWAP
  float gm0=0.0f;
  #pragma unroll
  for(unsigned i=0;i<TM;i++) {
    unsigned row=(mb0+i)*16+lane%16;
    float s=xs[row]*wscale;
    #pragma unroll
    for(unsigned j=0;j<TN;j++) {
      unsigned col0=(nb0+j)*16+(lane/16)*8;
      u4 bb=*(const u4 *)(bias+col0);
#if RESIDUAL
      u4 rr=*(const u4 *)(res+row*N+col0);
#endif
      u4 o;
      #pragma unroll
      for(unsigned q=0;q<4;q++) {
        unsigned short h0=bf(__builtin_fmaf(accum[i][j][2*q],s,frombf((unsigned short)(bb[q]&0xffffu))));
        unsigned short h1=bf(__builtin_fmaf(accum[i][j][2*q+1],s,frombf((unsigned short)(bb[q]>>16))));
#if RESIDUAL
        h0=bf(frombf((unsigned short)(rr[q]&0xffffu))+frombf(h0));
        h1=bf(frombf((unsigned short)(rr[q]>>16))+frombf(h1));
#endif
#if GOUT
        h0=bf(gelu(frombf(h0))); h1=bf(gelu(frombf(h1)));
        gm0=__builtin_fmaxf(gm0,__builtin_fmaxf(__builtin_fabsf(frombf(h0)),__builtin_fabsf(frombf(h1))));
#endif
        o[q]=(unsigned)h0|((unsigned)h1<<16);
      }
      *(u4 *)(out+row*N+col0)=o;
    }
  }
#if PMAX
  unsigned bits=__builtin_bit_cast(unsigned,gm0);
  #pragma unroll
  for(unsigned o=16;o>0;o/=2) { unsigned t=__builtin_amdgcn_ds_bpermute((int)((lane^o)*4),(int)bits); bits=bits>t?bits:t; }
  // partial[mt*NT+nt]: row tiles of image 0 come first (MT even, tiles never straddle images).
  if(lane==0) partial[mt*NT+nt]=bits;
#endif
#else
#if GELUMAX
  float gm0=0.0f;  // |gelu| maximum of this lane; rows of one tile never straddle images when ROWS_PER_IMAGE%(16*TM)==0
#endif
  #pragma unroll
  for(unsigned i=0;i<TM;i++) {
    unsigned row0=(mb0+i)*16+(lane/16)*8;
    float s[8];
    #pragma unroll
    for(unsigned v=0;v<8;v++) s[v]=xs[row0+v<M?row0+v:M-1]*wscale;
    #pragma unroll
    for(unsigned j=0;j<TN;j++) {
      unsigned col=(nb0+j)*16+lane%16;
      if(col<N && row0<M) {
        float bv=frombf(bias[col]);
        #pragma unroll
        for(unsigned v=0;v<8;v++) {
          unsigned row=row0+v;
          unsigned short h=bf(__builtin_fmaf(accum[i][j][v],s[v],bv));
#if RESIDUAL
          h=bf(frombf(res[row*N+col])+frombf(h));
#endif
          out[row*N+col]=h;
#if GELUMAX
          gm0=__builtin_fmaxf(gm0,__builtin_fabsf(frombf(bf(gelu(frombf(h))))));
#endif
        }
      }
    }
  }
#if GELUMAX
  // Order-free maximum of nonnegative floats: integer max of their bits.
  unsigned bits=__builtin_bit_cast(unsigned,gm0);
  #pragma unroll
  for(unsigned o=16;o>0;o/=2) { unsigned t=__builtin_amdgcn_ds_bpermute((int)((lane^o)*4),(int)bits); bits=bits>t?bits:t; }
  if(lane==0) __hip_atomic_fetch_max(&gmax[(mb0*16)/ROWS_PER_IMAGE],bits,__ATOMIC_RELAXED,__HIP_MEMORY_SCOPE_AGENT);
#endif
#endif
}
