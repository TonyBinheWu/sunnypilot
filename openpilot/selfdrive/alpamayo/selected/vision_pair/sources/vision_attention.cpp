
#define DEV __attribute__((device)) __attribute__((always_inline)) inline
typedef unsigned short u16;
typedef unsigned short u8 __attribute__((ext_vector_type(8)));
DEV u8 load_plain(const u16 *source,int head,int row,int dim) {
  if(row>=720 || dim>=72) return (u8){};
  return *(const u8 *)(source+(head*720+row)*72+dim);
}
DEV u8 load_eight(const u16 *source,int head,int row,int dim) {
  if(row>=720 || dim>=72) return (u8){};
  return *(const volatile u8 *)(source+(head*720+row)*72+dim);
}
typedef short s8 __attribute__((ext_vector_type(8)));
typedef float f8 __attribute__((ext_vector_type(8)));
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);
DEV float frombf(u16 x) { return __builtin_bit_cast(float, (unsigned)x << 16); }
DEV short tobf(float x) { unsigned b=__builtin_bit_cast(unsigned,x); return (b+0x7fff+((b>>16)&1))>>16; }
template<int offset> DEV float shuffle(float x) {
  return __builtin_bit_cast(float,__builtin_amdgcn_ds_swizzle(__builtin_bit_cast(int,x),offset));
}
DEV float maximum(float x) {
  x=__builtin_fmaxf(x,shuffle<0x201f>(x)); x=__builtin_fmaxf(x,shuffle<0x101f>(x));
  x=__builtin_fmaxf(x,shuffle<0x081f>(x)); x=__builtin_fmaxf(x,shuffle<0x041f>(x)); return x;
}
DEV float total(float x) {
  x+=shuffle<0x201f>(x); x+=shuffle<0x101f>(x); x+=shuffle<0x081f>(x); x+=shuffle<0x041f>(x); return x;
}
DEV f8 mma(s8 a,s8 b,f8 c) { return __builtin_amdgcn_wmma_f32_16x16x16_bf16_w32_gfx12(a,b,c); }
DEV int key_index(int row,int dim) {
  #if 0
  return ((row/16)*((72+15)/16)+dim/16)*256+(dim%16/4)*64+(row%16)*4+dim%4;
  #else
  return row*(((72+15)/16)*16+8)+dim;
  #endif
}
DEV float lane_read(float x, int source) {
  return __builtin_bit_cast(float,__builtin_amdgcn_ds_bpermute(source*4,__builtin_bit_cast(int,x)));
}
DEV f8 transpose_probability(f8 x, int lane) {
  // Exchange the three register row bits with the three low lane column bits.
  // Each pair needs one exchange; the other value stays in its source lane.
  for(int bit=1;bit<8;bit*=2) for(int j=0;j<8;j++) if(!(j&bit)) {
    float a=x[j], b=x[j|bit];
    float exchanged=lane_read((lane&bit)?a:b,lane^bit);
    x[j]=(lane&bit)?exchanged:a;
    x[j|bit]=(lane&bit)?b:exchanged;
  }
  // The high row and column bits both live in the lane index.
  int source=(lane&7)|((lane&8)<<1)|((lane&16)>>1);
  for(int j=0;j<8;j++) x[j]=lane_read(x[j],source);
  return x;
}
extern "C" __attribute__((global,amdgpu_flat_work_group_size(1,256),amdgpu_waves_per_eu(8,8)))
void alpamayo_online(u16 *out,const u16 *q,const u16 *k,const u16 *v
#if 0
,const float *mask
#endif
) {
  constexpr int H=16, KH=16, R=720, K=720, W=72, D=(W+15)/16;
  int thread=__ockl_get_local_id(0), lane=thread%32, wave=thread/32, block=__ockl_get_group_id(0);
  int group=block%((R+16*8-1)/(16*8));
  int tile=group*8+wave, head=block/((R+16*8-1)/(16*8)), kh=(head/H)*KH+(head%H)/(H/KH);
  int qr=tile*16+lane%16;
  __attribute__((shared,aligned(16))) short probabilities[8*16*(16+0)];
  #if 1
  // K rows and transposed V rows are 16-byte aligned for one vector access per lane.
  __attribute__((shared,aligned(16))) short shared_k2[2][32*(D*16+8)],shared_vt2[2][D*16*40];
  #endif
  short *prob=probabilities+wave*16*(16+0);
  s8 query[D];
  for(int d=0;d<D;d++) for(int i=0;i<8;i++) {
    int dim=d*16+(lane/16)*8+i;
    query[d][i]=qr<R && dim<W?q[(head*R+qr)*W+dim]:0;
  }
  // Row statistics live in the lanes that own a query row: lane%16 (both halves hold the same values).
  f8 accum[D]={}; float denom=0.0f, maxima=-__builtin_inff();
  int limit=(group+1)*8*16;
  int end=0?(K<limit?K:limit):K;
  // Double buffer: block j+1 is fetched into registers while block j is computed. Arithmetic is unchanged.
  constexpr int SLOTS=(32*D*16+256*8-1)/(256*8);
  u8 pk[SLOTS],pv[SLOTS];
  auto fetch=[&](int base) {
    for(int s=0;s<SLOTS;s++) { int index=thread*8+s*256*8; if(index<32*D*16) {
      int row=index/(D*16),dim=index%(D*16);
      pk[s]=load_plain(k,kh,base+row,dim); pv[s]=load_plain(v,kh,base+row,dim); } }
  };
  auto stage=[&](int buffer) {
    for(int s=0;s<SLOTS;s++) { int index=thread*8+s*256*8; if(index<32*D*16) {
      int row=index/(D*16),dim=index%(D*16);
      *(u8*)(shared_k2[buffer]+key_index(row,dim))=pk[s];
      for(int i=0;i<8;i++) shared_vt2[buffer][(dim+i)*40+row]=pv[s][i]; } }
  };
  fetch(0); stage(0);
  __builtin_amdgcn_fence(__ATOMIC_RELEASE,"workgroup"); __builtin_amdgcn_s_barrier();
  __builtin_amdgcn_fence(__ATOMIC_ACQUIRE,"workgroup");
  int buffer=0;
  for(int start=0;start<end;start+=32) {
    short *shared_k=shared_k2[buffer], *shared_vt=shared_vt2[buffer];
    bool more=start+32<end;
    if(more) fetch(start+32);
    if(tile*16<R) {  // waves whose 16 query rows are all padding only stage K/V
    f8 scores[32/16]={};
    for(int sub=0;sub<32/16;sub++) for(int d=0;d<D;d++) {
      s8 key=*(const s8*)(shared_k+key_index(sub*16+lane%16,d*16+(lane/16)*8));
      scores[sub]=mma(key,query[d],scores[sub]);
    }
    // K.Q^T: this lane holds query row tile*16+lane%16 and keys start+sub*16+(lane/16)*8+i, the PV operand layout.
    float localmax=-__builtin_inff();
    for(int sub=0;sub<32/16;sub++) for(int i=0;i<8;i++) {
      int col=start+sub*16+(lane/16)*8+i;
      scores[sub][i]=(start+32<=K || col<K)?scores[sub][i]*0.11785113019775792f:-__builtin_inff();
      localmax=__builtin_fmaxf(localmax,scores[sub][i]);
    }
    float next=__builtin_fmaxf(maxima,__builtin_fmaxf(localmax,shuffle<0x401f>(localmax)));
    float scale=next==-__builtin_inff()?1.0f:__builtin_exp2f((maxima-next)*1.4426950408889634f);
    f8 t;
    for(int i=0;i<8;i++) {
      for(int sub=0;sub<32/16;sub++)
        scores[sub][i]=next==-__builtin_inff()?0.0f:__builtin_exp2f((scores[sub][i]-next)*1.4426950408889634f);
      t[i]=scores[0][i]+scores[1][i];
      // Same tree as the original lane reduction: key c with c^8, then c^4, c^2, c^1.
      t[i]+=shuffle<0x401f>(t[i]);
    }
    float total_sum=((t[0]+t[4])+(t[2]+t[6]))+((t[1]+t[5])+(t[3]+t[7]));
    // x*1.0f==x exactly: skip the rescale when no row of this wave raised its maximum.
    if(__builtin_amdgcn_ballot_w32(scale!=1.0f)) for(int i=0;i<8;i++) {
      float row_scale=lane_read(scale,(lane/16)*8+i);
      for(int d=0;d<D;d++) accum[d][i]*=row_scale;
    }
    denom=denom*scale+total_sum; maxima=next;
    for(int sub=0;sub<32/16;sub++) {
    #if 1
    s8 probability;
    for(int i=0;i<8;i++) probability[i]=tobf(scores[sub][i]);
    #elif 0
    f8 transposed=transpose_probability(scores[sub],lane);
    s8 probability;
    for(int i=0;i<8;i++) probability[i]=tobf(transposed[i]);
    #else
    for(int i=0;i<8;i++) prob[((lane/16)*8+i)*(16+0)+lane%16]=tobf(scores[sub][i]);
    #if 0
    __builtin_amdgcn_fence(__ATOMIC_RELEASE,"wavefront"); __builtin_amdgcn_wave_barrier();
    __builtin_amdgcn_fence(__ATOMIC_ACQUIRE,"wavefront");
    #else
    __builtin_amdgcn_fence(__ATOMIC_RELEASE,"workgroup"); __builtin_amdgcn_s_barrier();
    __builtin_amdgcn_fence(__ATOMIC_ACQUIRE,"workgroup");
    #endif
    s8 probability;
    for(int i=0;i<8;i++) probability[i]=prob[(lane%16)*(16+0)+(lane/16)*8+i];
    #endif
    for(int d=0;d<D;d++) {
      s8 value=*(const s8*)(shared_vt+(d*16+lane%16)*40+sub*16+(lane/16)*8);
      accum[d]=mma(probability,value,accum[d]);
    }
    #if !0 && !1
    #if 0
    __builtin_amdgcn_fence(__ATOMIC_RELEASE,"wavefront"); __builtin_amdgcn_wave_barrier();
    __builtin_amdgcn_fence(__ATOMIC_ACQUIRE,"wavefront");
    #else
    __builtin_amdgcn_s_barrier();
    #endif
    #endif
    }
    }
    if(more) stage(buffer^1);
    // Block j+1 is visible, and every wave finished reading the buffer that block j+2 will replace.
    __builtin_amdgcn_fence(__ATOMIC_RELEASE,"workgroup"); __builtin_amdgcn_s_barrier();
    __builtin_amdgcn_fence(__ATOMIC_ACQUIRE,"workgroup");
    buffer^=1;
  }
  for(int d=0;d<D;d++) for(int i=0;i<8;i++) {
    int row=tile*16+(lane/16)*8+i;
    float row_denom=lane_read(denom,(lane/16)*8+i);
    if(row<R && d*16+lane%16<W) out[(head*R+row)*W+d*16+lane%16]=tobf(accum[d][i]/row_denom);
  }
}
