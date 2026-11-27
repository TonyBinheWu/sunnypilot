// LAUNCH 2 256
// Per-image maximum of nonnegative float partials (order-free): out[image]=max(partial[image*P .. image*P+P-1]).
#define P 675
extern "C" __attribute__((device)) unsigned long __ockl_get_local_id(unsigned);
extern "C" __attribute__((device)) unsigned long __ockl_get_group_id(unsigned);
extern "C" __attribute__((global,amdgpu_flat_work_group_size(256,256)))
void partial_max(unsigned *__restrict out,const unsigned *__restrict partial) {
  unsigned t=__ockl_get_local_id(0),g=__ockl_get_group_id(0);
  unsigned r=0;
  for(unsigned i=t;i<P;i+=256) { unsigned v=partial[g*P+i]; r=r>v?r:v; }
  #pragma unroll
  for(unsigned o=16;o>0;o/=2) { unsigned u=__builtin_amdgcn_ds_bpermute((int)(((t%32)^o)*4),(int)r); r=r>u?r:u; }
  __attribute__((shared)) unsigned red[8];
  if(t%32==0) red[t/32]=r;
  __builtin_amdgcn_fence(__ATOMIC_RELEASE,"workgroup"); __builtin_amdgcn_s_barrier(); __builtin_amdgcn_fence(__ATOMIC_ACQUIRE,"workgroup");
  if(t==0) { for(unsigned w=1;w<8;w++) r=r>red[w]?r:red[w]; out[g]=r; }
}
