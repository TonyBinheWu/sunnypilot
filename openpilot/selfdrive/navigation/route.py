"""Route-relative map pose and progress tracking."""
import numpy as np

MAX_LATITUDE = 85.05112878


def route_coordinates(route) -> np.ndarray:
  """A navRoute message as (longitude, latitude) rows."""
  return np.array([(c.longitude, c.latitude) for c in route.coordinates], dtype=np.float64).reshape((-1, 2))


# Training renders the map on the route rather than at the measured position:
# the ego is projected onto the route, the frame is centered there and headed along the route's tangent.
PROJECTION_WINDOW = (-30.0, 100.0)  # meters around the previous progress to search; a loop cannot capture the ego
HEADING_HALF_WINDOW = 50.0  # meters; the heading is the chord of the route this far behind and ahead


def cumulative_distance(route: np.ndarray) -> np.ndarray:
  """Haversine meters along [(longitude, latitude), ...]."""
  points = np.radians(route)
  (lon1, lat1), (lon2, lat2) = points[:-1].T, points[1:].T
  h = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
  return np.r_[0.0, np.cumsum(2 * 6371008.8 * np.arctan2(np.sqrt(h), np.sqrt(1 - h)))]


class RouteTracker:
  """Progress of the ego along a route, in meters, and the map pose at that progress."""

  def __init__(self, route: np.ndarray):
    self.route = np.asarray(route, dtype=np.float64).reshape((-1, 2))
    self.distance = cumulative_distance(self.route) if len(self.route) >= 2 else np.zeros(len(self.route))
    self.progress = -np.inf  # the first fix may land anywhere on the route
    self.origin = self.route[0] if len(self.route) else np.zeros(2)
    self.scale = np.array([111320.0 * np.cos(np.radians(self.origin[1])), 110540.0])
    self.path = (self.route - self.origin) * self.scale
    self.segments = np.diff(self.path, axis=0)
    self.bearings = np.degrees(np.arctan2(self.segments[:, 0], self.segments[:, 1]))

  def _candidates(self, longitude, latitude):
    if len(self.route) < 2:
      raise ValueError("Route needs at least two coordinates")
    point = (np.array([longitude, latitude]) - self.origin) * self.scale
    near = np.flatnonzero((self.distance[1:] >= self.progress + PROJECTION_WINDOW[0]) & (self.distance[:-1] <= self.progress + PROJECTION_WINDOW[1]))
    if not len(near):
      near = np.arange(len(self.segments))
    a, ab = self.path[near], self.segments[near]
    along = np.clip(((point - a) * ab).sum(axis=1) / np.maximum((ab * ab).sum(axis=1), 1e-12), 0, 1)
    error = np.linalg.norm(a + along[:, None] * ab - point, axis=1)
    progress = self.distance[near] + along * (self.distance[near + 1] - self.distance[near])
    return near, error, progress

  def project(self, longitude: float, latitude: float) -> float:
    """Advance to the nearest spot within the route progress window."""
    _, error, progress = self._candidates(longitude, latitude)
    self.progress = max(self.progress, progress[error.argmin()])
    return self.progress

  def pose(self, progress: float) -> tuple[float, float, float]:
    """(longitude, latitude, bearing) on the route at a progress, headed along the +-50m chord."""
    ends = np.clip([progress - HEADING_HALF_WINDOW, progress, progress + HEADING_HALF_WINDOW], 0, self.distance[-1])
    (lon0, lon, lon1), (lat0, lat, lat1) = (np.interp(ends, self.distance, self.route[:, axis]) for axis in (0, 1))
    bearing = np.degrees(np.arctan2((lon1 - lon0) * np.cos(np.radians(lat0)), lat1 - lat0)) % 360
    return float(lon), float(lat), float(bearing)

  def snap(self, longitude: float, latitude: float) -> tuple[float, float, float]:
    return self.pose(self.project(longitude, latitude))

  def match_pose(self, longitude, latitude, advance=0., max_distance=50., *, course=None):
    """Compare segment hypotheses before committing monotonic progress. Course is measured clockwise from north."""
    near, error, progress = self._candidates(longitude, latitude)
    usable = (error <= max_distance) & (self.distance[near + 1] - self.distance[near] >= .5)
    if not usable.any():
      return 'offRoute', None
    # Squared normalized residuals approximate independent position and course errors.
    # Never snap across the road to a distant segment just because its heading fits.
    usable &= error <= error[usable].min() + 12.
    score = (error / 8.) ** 2
    if course is not None:
      angle = np.abs((self.bearings[near] - course + 180.) % 360. - 180.)
      usable &= angle <= 65.
      if not usable.any():
        return 'headingConflict', None
      score += (angle / 25.) ** 2
    best = np.where(usable, score, np.inf).argmin()
    # Adjacent polyline edges near the same route progress describe the same maneuver.
    rivals = usable & (np.abs(progress - progress[best]) > 40.)
    if np.any(rivals & (score <= score[best] + 2.)):
      return 'ambiguous', None
    accepted = max(self.progress, progress[best])
    pose = self.pose(accepted + advance)
    lon, lat, _ = pose
    distance = np.hypot((lon - longitude) * 111320 * np.cos(np.radians(lat)), (lat - latitude) * 110540)
    if not np.isfinite(distance) or distance > max_distance:
      return 'offRoute', None
    self.progress = accepted
    return 'matched', pose

  def update_pose(self, longitude: float, latitude: float, advance: float = 0., max_distance: float = 50.) -> tuple[float, float, float] | None:
    return self.match_pose(longitude, latitude, advance, max_distance)[1]

  def contradicts_turn(self, maneuver, ahead):
    """Withhold a left/right instruction only when the route bends clearly the other way at that step."""
    if maneuver not in ('turn left', 'turn right'):
      return False
    window = self.progress + ahead + np.array([-16., -4., 4., 16.])
    if window[0] < 0. or window[-1] > self.distance[-1]:
      return False
    points = np.column_stack([np.interp(window, self.distance, axis) for axis in self.path.T])
    incoming, outgoing = points[1] - points[0], points[3] - points[2]
    if min(np.linalg.norm(incoming), np.linalg.norm(outgoing)) < 9.:
      return False
    angle = np.degrees(np.arctan2(*outgoing) - np.arctan2(*incoming))
    angle = (angle + 180.) % 360. - 180.
    return 45. < abs(angle) < 140. and (angle > 0.) != (maneuver == 'turn right')
