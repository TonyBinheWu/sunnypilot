// LAUNCH 1056 64
// Exact prefill causal attention reading K and V from the (2,1,8,CAP,128) KV cache. Variant final.
#define ROWS 576
#define CAP 2304
#define DEV __attribute__((device)) __attribute__((always_inline)) inline
typedef unsigned short u16;
typedef short s8 __attribute__((ext_vector_type(8)));
typedef float f8 __attribute__((ext_vector_type(8)));
typedef __attribute__((address_space(1))) s8 gs8;
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);
DEV short tobf(float x) { unsigned b=__builtin_bit_cast(unsigned,x); return (b+0x7fff+((b>>16)&1))>>16; }
DEV float swap16(float x) {
#if 0==2
  return __builtin_bit_cast(float,__builtin_amdgcn_permlanex16(__builtin_nondeterministic_value(0),__builtin_bit_cast(int,x),0x76543210,0xfedcba98,false,false));
#elif 0
  return __builtin_bit_cast(float,__builtin_amdgcn_permlanex16(__builtin_bit_cast(int,x),__builtin_bit_cast(int,x),0x76543210,0xfedcba98,false,false));
#else
  return __builtin_bit_cast(float,__builtin_amdgcn_ds_swizzle(__builtin_bit_cast(int,x),0x401f));
#endif
}
DEV f8 mma(s8 a,s8 b,f8 c) { return __builtin_amdgcn_wmma_f32_16x16x16_bf16_w32_gfx12(a,b,c); }
DEV float lane_read(float x, int source) {
  return __builtin_bit_cast(float,__builtin_amdgcn_ds_bpermute(source*4,__builtin_bit_cast(int,x)));
}
// The compiler lowers __builtin_exp2f(d*C) to this sequence (denormal-safe scaling below -126).
DEV float exp2_exact(float d) {
  const float C=1.4426950408889634f;
  float t=d*C; bool s=t<-126.0f;
  return __builtin_amdgcn_exp2f(__builtin_fmaf(C,d,s?64.0f:0.0f))*(s?0x1p-64f:1.0f);
}
extern "C" __attribute__((global,amdgpu_flat_work_group_size(1,64)))
void agent_prefill_cache_attention(u16 *out,const u16 *q,const u16 *kv) {
#pragma clang fp contract(off)
  constexpr int H=16, KH=8, R=ROWS, K=ROWS, W=128, D=8, WAVES=64/32;
  int thread=__ockl_get_local_id(0), lane=thread%32, wave=__builtin_amdgcn_readfirstlane(thread/32), block=__ockl_get_group_id(0);
  int head, tile;
  { int kvh=block%KH; tile=(ROWS/16-1)-block/KH; head=kvh*2+wave; }
  __attribute__((shared)) int occupancy_pad[12800/4];  // limits resident waves (fewer waves thrash caches less)
  if(__builtin_amdgcn_readfirstlane(block)==0x7fffffff) { volatile int *pp=occupancy_pad; pp[thread]=thread; }  // never taken; keeps the allocation
  if(tile*16>=R) return;
  int kh=head/(H/KH);
  int qr=tile*16+lane%16;
  s8 query[D];
  for(int d=0;d<D;d++) for(int i=0;i<8;i++) {
    int dim=d*16+(lane/16)*8+i;
    query[d][i]=q[(head*R+qr)*W+dim];
  }
  const u16 *kbase=kv+(long)kh*CAP*W, *vbase=kv+(long)(KH+kh)*CAP*W;
  // Lane address for the K operand (row = key lane%16, dims (lane/16)*8) and the transposed V load.
#if 1
  // Uniform block base (scalar) plus a fixed 32-bit per-lane byte offset: global_load saddr mode, no 64-bit VALU adds.
  const unsigned koff=((lane%16)*W+(lane/16)*8)*2, voff=(((lane/16)*8+lane%8)*W+((lane/8)%2)*8)*2;
#define KADDR(row,dim) ((const gs8*)((const char*)(kbase+(row)*W+(dim))+ko))
#define VADDR(row,dim) ((gs8*)((const char*)(vbase+(row)*W+(dim))+vo))
#else
  const u16 *kp=kbase+(lane%16)*W+(lane/16)*8;
  const u16 *vp=vbase+((lane/16)*8+lane%8)*W+((lane/8)%2)*8;
#define KADDR(row,dim) ((const gs8*)(kp+(row)*W+(dim)))
#define VADDR(row,dim) ((gs8*)(vp+(row)*W+(dim)))
#endif
  f8 accum[D]={}; float denom=0.0f, maxima=-__builtin_inff();
  int end=(tile*16+15)/32*32+32;  // blocks after the one holding this wave's diagonal are fully masked
#if 0 && 1
  unsigned ko=koff, vo=voff;
#endif
#if 0
  s8 keys[2][D];
  for(int sub=0;sub<2;sub++) for(int d=0;d<D;d++) keys[sub][d]=*KADDR(sub*16,d*16);
#endif
#if 1 && !0
  unsigned ko=koff, vo=voff;
#endif
  #pragma unroll 1
  for(int start=0;start<end;start+=32) {
#if 1
    // Keep the lane offsets opaque so the compiler selects scalar-base addressing instead of hoisted 64-bit pointers.
    asm volatile("" : "+v"(ko), "+v"(vo));
#endif
#if 0
    s8 value[D][2];
    if(0) {
      for(int d=0;d<D;d++) for(int sub=0;sub<2;sub++)
        value[d][sub]=__builtin_amdgcn_global_load_tr_b128_v8i16(VADDR(start+sub*16,d*16));
      __builtin_amdgcn_sched_barrier(0);
    }
    f8 scores[2]={};
    for(int sub=0;sub<2;sub++) for(int d=0;d<D;d++) scores[sub]=mma(keys[sub][d],query[d],scores[sub]);
    __builtin_amdgcn_sched_barrier(0);
    if(!0) {
      for(int d=0;d<D;d++) for(int sub=0;sub<2;sub++)
        value[d][sub]=__builtin_amdgcn_global_load_tr_b128_v8i16(VADDR(start+sub*16,d*16));
      __builtin_amdgcn_sched_barrier(0);
    }
#else
    f8 scores[2]={};
    for(int sub=0;sub<2;sub++) for(int d=0;d<D;d++) {
      s8 key=*KADDR(start+sub*16,d*16);
      scores[sub]=mma(key,query[d],scores[sub]);
    }
    __builtin_amdgcn_sched_barrier(0);
    s8 value[D][2];
    for(int d=0;d<D;d++) for(int sub=0;sub<2;sub++)
      value[d][sub]=__builtin_amdgcn_global_load_tr_b128_v8i16(VADDR(start+sub*16,d*16));
    __builtin_amdgcn_sched_barrier(0);
#endif
    bool diagonal=start+32>=end;
    if(diagonal) {
      for(int sub=0;sub<2;sub++) for(int i=0;i<8;i++) {
        int row=tile*16+lane%16, col=start+sub*16+(lane/16)*8+i;
        scores[sub][i]=(col<K && col<=row)?scores[sub][i]*0.08838834764831845f:-__builtin_inff();
      }
    } else {
      for(int sub=0;sub<2;sub++) for(int i=0;i<8;i++) scores[sub][i]=scores[sub][i]*0.08838834764831845f;
    }
    float localmax=-__builtin_inff();
    for(int i=0;i<8;i++) localmax=__builtin_fmaxf(localmax,__builtin_fmaxf(scores[0][i],scores[1][i]));
    float next=__builtin_fmaxf(maxima,__builtin_fmaxf(localmax,swap16(localmax)));
    float scale;
    f8 sums;
    if(__builtin_amdgcn_ballot_w32(next==-__builtin_inff())) {
      scale=next==-__builtin_inff()?1.0f:exp2_exact(maxima-next);
      for(int i=0;i<8;i++) {
        scores[0][i]=next==-__builtin_inff()?0.0f:exp2_exact(scores[0][i]-next);
        scores[1][i]=next==-__builtin_inff()?0.0f:exp2_exact(scores[1][i]-next);
      }
    } else {
      scale=exp2_exact(maxima-next);
#if 1
      f8 t0,t1; float low=0.0f;
      for(int i=0;i<8;i++) {
        t0[i]=(scores[0][i]-next)*1.4426950408889634f; t1[i]=(scores[1][i]-next)*1.4426950408889634f;
        low=__builtin_fminf(low,__builtin_fminf(t0[i],t1[i]));
      }
      if(__builtin_amdgcn_ballot_w32(!(low>=-126.0f))) {
        for(int i=0;i<8;i++) { scores[0][i]=exp2_exact(scores[0][i]-next); scores[1][i]=exp2_exact(scores[1][i]-next); }
      } else {
        for(int i=0;i<8;i++) { scores[0][i]=__builtin_amdgcn_exp2f(t0[i]); scores[1][i]=__builtin_amdgcn_exp2f(t1[i]); }
      }
#else
      for(int i=0;i<8;i++) { scores[0][i]=exp2_exact(scores[0][i]-next); scores[1][i]=exp2_exact(scores[1][i]-next); }
#endif
    }
    for(int i=0;i<8;i++) {
      sums[i]=scores[0][i]+scores[1][i];
      sums[i]+=swap16(sums[i]);
    }
    for(int i=0;i<4;i++) sums[i]+=sums[i+4];
    for(int i=0;i<2;i++) sums[i]+=sums[i+2];
    float total_sum=sums[0]+sums[1];
    denom=__builtin_fmaf(denom,scale,total_sum);
    maxima=next;
#if 1
    // Rows whose scale is 1 keep their values (x*1.0f==x); each register element i holds rows i and 8+i.
    unsigned changed=__builtin_amdgcn_ballot_w32(scale!=1.0f);
    if(changed) for(int i=0;i<8;i++) if(changed&((1u<<i)|(1u<<(8+i)))) {
      float row_scale=lane_read(scale,(lane/16)*8+i);
      for(int d=0;d<D;d++) accum[d][i]*=row_scale;
    }
#else
    if(__builtin_amdgcn_ballot_w32(scale!=1.0f)) for(int i=0;i<8;i++) {
      float row_scale=lane_read(scale,(lane/16)*8+i);
      for(int d=0;d<D;d++) accum[d][i]*=row_scale;
    }
#endif
#if 0==1
    __builtin_amdgcn_sched_barrier(0);
    for(int sub=0;sub<2;sub++) for(int d=0;d<D;d++) keys[sub][d]=*KADDR(start+32+sub*16,d*16);
    __builtin_amdgcn_sched_barrier(0);
#endif
    for(int sub=0;sub<2;sub++) {
      s8 probability;
      for(int i=0;i<8;i++) probability[i]=tobf(scores[sub][i]);
      for(int d=0;d<D;d++) accum[d]=mma(probability,value[d][sub],accum[d]);
#if 0==2
      // The next block's K half replaces the V half just consumed (the last prefetch reads unused cache rows < CAP).
      __builtin_amdgcn_sched_barrier(0);
      for(int d=0;d<D;d++) keys[sub][d]=*KADDR(start+32+sub*16,d*16);
      __builtin_amdgcn_sched_barrier(0);
#endif
    }
  }
  for(int i=0;i<8;i++) {
    int row=tile*16+(lane/16)*8+i;
    float row_denom=lane_read(denom,(lane/16)*8+i);
    for(int d=0;d<D;d++) if(row<R)
      out[(head*R+row)*W+d*16+lane%16]=tobf(accum[d][i]/row_denom);
  }
}
