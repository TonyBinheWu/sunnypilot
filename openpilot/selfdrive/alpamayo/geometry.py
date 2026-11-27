"""Reference nominal 120/30 degree projection using measured mounting rotations."""
from functools import lru_cache
import json
import math

import numpy as np
from scipy.ndimage import map_coordinates
from scipy.spatial.transform import Rotation

VIEW = np.array([[0., 1., 0.], [0., 0., 1.], [1., 0., 0.]])


@lru_cache(maxsize=2)
def lens_rays(camera, geometry_json):
  src = json.loads(geometry_json)['cameras'][str(camera)]
  w, h = src['prepared_size']
  left, top, right, bottom = src['content_box']
  fx, fy = src['focal_pixels']
  if src['projection'] not in ('equidistant', 'pinhole') or min(fx, fy, right-left, bottom-top) <= 0:
    raise ValueError('Invalid source lens geometry')
  yy, xx = np.mgrid[:h, :w]
  fov = src.get('output_fov', 120 if camera == 1 else 30)  # degrees across the model image; NVIDIA's rig is 120/30
  fraction = fx*math.radians(fov)/w if src['projection'] == 'equidistant' else 2*fx*math.tan(math.radians(fov/2))/w
  tx, ty = (xx-(w-1)/2)*fraction/fx, (yy-(h-1)/2)*fraction/fy
  radius = np.hypot(tx, ty)
  theta = radius if src['projection'] == 'equidistant' else np.arctan(radius)
  scale = np.divide(np.sin(theta), radius, out=np.ones_like(radius), where=radius > 0)
  rays = np.stack([tx*scale, ty*scale, np.cos(theta)], axis=-1)
  rays.flags.writeable = False
  return rays


@lru_cache(maxsize=8)
def coordinates(source_shape, camera, geometry_json, rpy, wide_rpy):
  src = json.loads(geometry_json)['cameras'][str(camera)]
  left, top, right, bottom = src['content_box']
  fx, fy = src['focal_pixels']
  cx, cy = src['principal_point']
  rays = lens_rays(camera, geometry_json)
  rotation = Rotation.from_euler('xyz', rpy).as_matrix()
  if camera == 1:
    rotation = Rotation.from_euler('xyz', wide_rpy).as_matrix() @ rotation
  rays = rays @ (VIEW @ rotation @ VIEW.T).T
  radial = np.hypot(rays[..., 0], rays[..., 1])
  theta = np.arctan2(radial, rays[..., 2])
  radius = theta if src['projection'] == 'equidistant' else np.tan(theta)
  factor = np.divide(radius, radial, out=np.ones_like(radius), where=radial > 1e-12)
  sx, sy = cx+fx*rays[..., 0]*factor, cy+fy*rays[..., 1]*factor
  if not np.isfinite(rays).all() or (src['projection'] == 'pinhole' and (rays[..., 2] <= 0).any()):
    raise ValueError('Calibrated rays are invalid for the source lens')
  # The nominal 120/30 views must lie inside the source image. A configured output_fov (the lenses' native 180/60
  # coverage) may extend past it after the mount rotation; those pixels repeat the image edge, as in the training views.
  if 'output_fov' not in src and ((rays[..., 2] <= 0).any() or
                                  sx.min() < left or sx.max() > right-1 or sy.min() < top or sy.max() > bottom-1):
    raise ValueError('Calibrated rays exceed source image coverage')
  source_h, source_w = source_shape
  return (sy-top+.5)*source_h/(bottom-top)-.5, (sx-left+.5)*source_w/(right-left)-.5


def calibrated_image(array, camera, geometry, calibration):
  if camera not in (1, 6) or array.dtype != np.uint8 or array.ndim != 3 or array.shape[0] != 3:
    raise ValueError('Expected front-camera uint8 CHW RGB')
  sy, sx = coordinates(tuple(array.shape[-2:]), camera, json.dumps(geometry, sort_keys=True),
                       tuple(calibration['rpyCalib']), tuple(calibration['wideFromDeviceEuler']))
  return np.stack([map_coordinates(channel, (sy, sx), order=1, mode='nearest', prefilter=False) for channel in array]).astype(np.uint8)
