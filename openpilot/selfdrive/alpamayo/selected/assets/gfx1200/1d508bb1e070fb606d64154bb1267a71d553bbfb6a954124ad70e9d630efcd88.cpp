// LAUNCH 192 256
#define WAVES 8
#define THREADS 256
#define WPE
#define PMAX 0

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
typedef __attribute__((address_space(1))) s8 gs8;
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
extern "C" __attribute__((global,amdgpu_flat_work_group_size(1,THREADS)WPE))
void alpamayo_online(u16 *out,const u16 *q,const u16 *k,const u16 *v
#if PMAX
,float *partial
#endif
) {
  // Same arithmetic as the staged kernel. Each wave reads its K operand and the transposed V operand straight from
  // memory (gfx12 transposing load) instead of a shared-memory copy; waves no longer synchronize.
  constexpr int H=16, KH=16, R=720, K=720, W=72, D=(W+15)/16;
  int thread=__ockl_get_local_id(0), lane=thread%32, wave=__builtin_amdgcn_readfirstlane(thread/32), block=__ockl_get_group_id(0);
  int group=block%((R+16*WAVES-1)/(16*WAVES));
  int tile=group*WAVES+wave, head=block/((R+16*WAVES-1)/(16*WAVES)), kh=(head/H)*KH+(head%H)/(H/KH);
  if(tile*16>=R) {  // all 16 query rows are padding
#if PMAX
    if(lane==0) partial[block*WAVES+wave]=0.0f;
#endif
    return;
  }
  int qr=tile*16+lane%16;
  s8 query[D];
  for(int d=0;d<D;d++) for(int i=0;i<8;i++) {
    int dim=d*16+(lane/16)*8+i;
    query[d][i]=qr<R && dim<W?q[(head*R+qr)*W+dim]:0;
  }
  const u16 *kbase=k+(long)kh*R*W, *vbase=v+(long)kh*R*W;
  // Per-lane byte offsets. K operand: key row lane%16, dims (lane/16)*8.. ; V: the transposing load takes key row
  // (lane/16)*8+lane%8 and dim half (lane/8)%2 and returns dim lane%16, keys (lane/16)*8.. per lane.
  // The last fragment holds dims 64-71 only: all lanes address dims 64-71 (in bounds). K lanes of dims 72-79 are zeroed;
  // V results of dims 72-79 only reach outputs that are never written.
  unsigned ko=((lane%16)*W+(lane/16)*8)*2, ko4=((lane%16)*W)*2;
  unsigned vo=(((lane/16)*8+lane%8)*W+((lane/8)%2)*8)*2, vo4=(((lane/16)*8+lane%8)*W)*2;
#define KADDR(row,dim,off) ((const gs8*)((const char*)(kbase+(row)*W+(dim))+(off)))
#define VADDR(row,dim,off) ((gs8*)((const char*)(vbase+(row)*W+(dim))+(off)))
  // Row statistics live in the lanes that own a query row: lane%16 (both halves hold the same values).
  f8 accum[D]={}; float denom=0.0f, maxima=-__builtin_inff();
  int end=K;
  #pragma unroll 1
  for(int start=0;start<end;start+=32) {
    asm volatile("" : "+v"(ko), "+v"(vo), "+v"(ko4), "+v"(vo4));
    f8 scores[32/16]={};
    s8 value[D][32/16];
    for(int sub=0;sub<32/16;sub++) {
      if(start+sub*16<K) {
        for(int d=0;d<D;d++) {
          s8 key;
          if(d*16+8<W) key=*KADDR(start+sub*16,d*16,ko);
          else { key=*KADDR(start+sub*16,d*16,ko4); key=lane<16?key:(s8){}; }
          scores[sub]=mma(key,query[d],scores[sub]);
        }
        for(int d=0;d<D;d++)
          value[d][sub]=__builtin_amdgcn_global_load_tr_b128_v8i16(d*16+8<W?VADDR(start+sub*16,d*16,vo):VADDR(start+sub*16,d*16,vo4));
      } else {
        for(int d=0;d<D;d++) { scores[sub]=mma((s8){},query[d],scores[sub]); value[d][sub]=(s8){}; }
      }
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
      s8 probability;
      for(int i=0;i<8;i++) probability[i]=tobf(scores[sub][i]);
      for(int d=0;d<D;d++) accum[d]=mma(probability,value[d][sub],accum[d]);
    }
  }
  float top=0.0f;
  for(int d=0;d<D;d++) for(int i=0;i<8;i++) {
    int row=tile*16+(lane/16)*8+i;
    float row_denom=lane_read(denom,(lane/16)*8+i);
    if(row<R && d*16+lane%16<W) {
      short o=tobf(accum[d][i]/row_denom);
      out[(head*R+row)*W+d*16+lane%16]=o;
#if PMAX
      top=__builtin_fmaxf(top,__builtin_fabsf(frombf((u16)o)));
#endif
    }
  }
#if PMAX
  // Per-wave maximum of |out| (order-free): partial[block*WAVES+wave]; blocks of image 0 come first.
  top=maximum(top); top=__builtin_fmaxf(top,shuffle<0x401f>(top));
  if(lane==0) partial[block*WAVES+wave]=top;
#endif
}
