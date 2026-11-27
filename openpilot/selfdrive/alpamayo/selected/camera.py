"""Optional portable sampler using the shared exact 120/30-degree ray geometry."""
import ctypes
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import os
import numpy as np
from openpilot.selfdrive.alpamayo.geometry import coordinates


@lru_cache(maxsize=1)
def library(cache_dir):
  source = Path(__file__).with_name('native_warp.c')
  compiler = shutil.which('clang') or shutil.which('cc')
  if compiler is None:
    raise RuntimeError('A host C compiler is required for the camera sampler')
  flags = ['-O3','-shared','-fPIC','-ffp-contract=off','-std=c11']
  version = subprocess.check_output([compiler,'--version'])
  digest = hashlib.sha256(source.read_bytes()+version+platform.machine().encode()+repr(flags).encode()).hexdigest()
  cache = Path(cache_dir)/'native-warp'
  cache.mkdir(parents=True,exist_ok=True)
  output = cache/(digest+'.so')
  if not output.exists():
    with tempfile.TemporaryDirectory(dir=cache) as directory:
      temporary = Path(directory)/'warp.so'
      subprocess.run([compiler,*flags,str(source),'-o',str(temporary)],check=True)
      os.replace(temporary,output)
  lib = ctypes.CDLL(str(output))
  lib.warp_u8.argtypes = [ctypes.c_void_p]*4+[ctypes.c_size_t]*4
  lib.warp_u8.restype = None
  lib.warp_hwc_u8.argtypes = [ctypes.c_void_p]*4+[ctypes.c_size_t]*3
  lib.warp_hwc_u8.restype = None
  return lib


@lru_cache(maxsize=8)
def maps(shape, camera, geometry_json, rotation, wide_rotation):
  sy,sx = coordinates(shape,camera,geometry_json,rotation,wide_rotation)
  h,w = shape
  sx,sy = np.clip(sx,0,w-1),np.clip(sy,0,h-1)
  xy = np.stack([sx,sy],axis=-1)
  offsets = np.floor(xy).astype(np.int32)
  return offsets,xy-offsets


CROP_MARGIN = 8  # luma pixels kept around the sampled region; the colour conversion's chroma filter reaches 2


@lru_cache(maxsize=8)
def crop_maps(shape, camera, geometry_json, rotation, wide_rotation):
  """Even-aligned source crop around every sampled pixel, and the sample offsets relative to it."""
  offsets,fractions = maps(shape,camera,geometry_json,rotation,wide_rotation)
  h,w = shape
  x0,y0 = (max(int(offsets[...,i].min())-CROP_MARGIN,0)//2*2 for i in (0,1))
  x1,y1 = (min((int(offsets[...,i].max())+2+CROP_MARGIN+1)//2*2,limit) for i,limit in ((0,w),(1,h)))
  if (x1-x0) % 16 == 0:  # libswscale converts widths that are multiples of 16 on another path with other rounding
    x0,x1 = (x0,x1+2) if x1+2 <= w else (x0-2,x1)
  # A column crop changes libswscale's row path for some widths; full-width row crops convert each row unchanged.
  rect = ((y0,y1,x0,x1) if (x1-x0) % 16 and crop_exact((h,w),(y0,y1,x0,x1)) else
          (y0,y1,0,w) if crop_exact((h,w),(y0,y1,0,w)) else (0,h,0,w))
  return rect,np.ascontiguousarray(offsets-np.array([rect[2],rect[0]],dtype=np.int32)),fractions


def rgb24(nv12):
  import av
  return av.VideoFrame.from_ndarray(nv12,format='nv12').to_ndarray(format='rgb24')


def nv12_crop(nv12, rect):
  y0,y1,x0,x1 = rect
  h = nv12.shape[0]*2//3
  return np.concatenate([nv12[y0:y1,x0:x1],nv12[h+y0//2:h+y1//2,x0:x1]])


@lru_cache(maxsize=16)
def crop_exact(shape, rect):
  """Check once per crop that its conversion equals full-frame conversion away from the crop edges."""
  h,w = shape
  frame = np.random.default_rng(0).integers(0,256,(h*3//2,w),dtype=np.uint8)
  y0,y1,x0,x1 = rect
  inner = lambda rgb,dy,dx: rgb[dy+CROP_MARGIN-2:dy+y1-y0-CROP_MARGIN+2,dx+CROP_MARGIN-2:dx+x1-x0-CROP_MARGIN+2]
  return bool(np.array_equal(inner(rgb24(nv12_crop(frame,rect)),0,0),inner(rgb24(frame),y0,x0)))


def nv12_image(nv12, camera, geometry, calibration, *, cache_dir):
  """Sample an NV12 camera frame. Only the sampled region is converted to RGB; the output equals full-frame conversion."""
  h,w = nv12.shape[0]*2//3,nv12.shape[1]
  if nv12.dtype != np.uint8 or nv12.ndim != 2 or h*3//2 != nv12.shape[0] or h % 2 or w % 2:
    raise ValueError('Expected a uint8 NV12 frame')
  rect,offsets,fractions = crop_maps((h,w),camera,json.dumps(geometry,sort_keys=True),tuple(calibration['rpyCalib']),
                                     tuple(calibration['wideFromDeviceEuler']) if camera == 1 else ())
  y0,y1,x0,x1 = rect
  rgb = np.ascontiguousarray(rgb24(nv12_crop(nv12,rect) if rect != (0,h,0,w) else nv12))
  out = np.empty((3,*offsets.shape[:2]),dtype=np.uint8)
  library(str(cache_dir)).warp_hwc_u8(rgb.ctypes.data,out.ctypes.data,offsets.ctypes.data,fractions.ctypes.data,offsets.size//2,x1-x0,y1-y0)
  return out


def calibrated_image(array, camera, geometry, calibration, *, cache_dir):
  """Sample a uint8 NV12 frame or contiguous RGB, planar CHW or interleaved HWC, into a planar CHW image."""
  if array.ndim == 2:
    return nv12_image(array,camera,geometry,calibration,cache_dir=cache_dir)
  if array.dtype != np.uint8 or array.ndim != 3 or not array.flags.c_contiguous or (array.shape[0] == 3) == (array.shape[-1] == 3):
    raise ValueError('Native sampler requires contiguous uint8 CHW or HWC RGB')
  interleaved = array.shape[-1] == 3
  h,w = array.shape[:2] if interleaved else array.shape[-2:]
  offsets,fractions = maps((h,w),camera,json.dumps(geometry,sort_keys=True),
                          tuple(calibration['rpyCalib']),tuple(calibration['wideFromDeviceEuler']) if camera == 1 else ())
  out = np.empty((3,*offsets.shape[:2]),dtype=np.uint8)
  lib = library(str(cache_dir))
  if interleaved:
    lib.warp_hwc_u8(array.ctypes.data,out.ctypes.data,offsets.ctypes.data,fractions.ctypes.data,offsets.size//2,w,h)
  else:
    lib.warp_u8(array.ctypes.data,out.ctypes.data,offsets.ctypes.data,fractions.ctypes.data,offsets.size//2,h*w,w,h)
  return out
