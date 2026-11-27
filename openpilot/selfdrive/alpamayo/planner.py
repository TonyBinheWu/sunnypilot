"""Select a time-aligned Alpamayo trajectory; the driving action comes only from Alpamayo plans.

A plan is usable when it was ready within MAX_LATENCY of its camera query and while that query is younger than
MAX_PLAN_AGE, whatever the scheduling mode. Bad or late packets are ignored; the current plan simply ages out.
"""
import math
from collections import deque
import numpy as np

PERIOD = 500_000_000
FREE = 0  # Free-running: each prediction starts when the previous one finishes.
PERIODS = (FREE, 100_000_000, 250_000_000, 500_000_000)
FREE_WINDOW = 400_000_000  # Free-running supervisor: slot bookkeeping deadline after selection.
MAX_LATENCY = 750_000_000  # Camera query to plan ready; complex scenes reason for up to ~400 ms in the car.
MAX_PLAN_AGE = 1_500_000_000  # A plan drives while its camera query is at most this old; its horizon is 6.4 s.
# In the car a plan is ready 350-550 ms after its query, and one superseded 250 ms slot leaves a 500 ms query gap.
CONSECUTIVE_GAP = 1_000_000_000  # Consecutive plans have queries at most this far apart (two superseded slots).
HANDOFF_GRACE = 100_000_000  # modeld reads plans once per 20 Hz camera frame, after its own model run; allow two frames.
T = np.arange(65) * .1
ACTION_TIMES = np.arange(22)*.1
# Path tracking: Alpamayo corrects only about half of a heading or lateral error in its own plan, and plans drive
# 0.2-0.5 s after their camera frame. The planner therefore keeps each plan's path fixed to the road (odometry since
# its camera query) and steers to a point LOOKAHEAD_S ahead on it from the pose expected after the steering delay.
LOOKAHEAD_S = 1.5
T_PATH = np.arange(65)*.1  # plan path times including the query pose
MIN_LOOKAHEAD = 8.  # m; a longer lookahead halves the response to plan-to-plan jitter (curvature = 2 y / L^2)
# The pose after the steering delay is predicted with the measured curvature (odometry heading change over
# CURVATURE_WINDOW). Predicting it with the tracker's own last command made consecutive commands alternate.
CURVATURE_WINDOW = .3  # s
COMMAND_TAU = .25  # s, first-order smoothing of the tracked curvature (modelV2 runs at 20 Hz)
POSE_EXTRAPOLATION_NS = 300_000_000  # odometry extrapolation after its newest sample
ODOMETRY_S = 3.  # odometry history kept, longer than the latest plan's age


LOAD_TIMEOUT_S = 240.  # the big driving model gets 60 s; Alpamayo loads its weights and runs a warmup in 70 to 120 s
STABLE_S = 3.  # plans must stay usable this long before Alpamayo takes over
GAP_FAIL_S = 2.  # road gaps without a usable plan lasted 0.25 to 1.2 s (2026-11-24); the small model drives through them


class BigModelState:
  """Latch fallback on an unusable engaged frame. Activation requires stable plans and idle control axes."""
  LOADING, ACTIVE, FAILED = 'loading', 'active', 'failed'

  def __init__(self, now_s):
    self.state = self.LOADING
    self.started = self.last_plan = now_s
    self.usable_since = None

  def update(self, now_s, plan_usable, engaged):
    """Returns True when Alpamayo gives this frame's action."""
    if plan_usable:
      self.last_plan = now_s
    # The first plans after a load can be followed by a gap of several seconds (first-use GPU work).
    self.usable_since = (now_s if self.usable_since is None else self.usable_since) if plan_usable else None
    stable = self.usable_since is not None and now_s-self.usable_since >= STABLE_S
    if self.state == self.LOADING:
      if stable and not engaged:
        self.state = self.ACTIVE
      elif now_s-self.started > LOAD_TIMEOUT_S:
        self.state = self.FAILED
    elif self.state == self.ACTIVE:
      if (engaged and not plan_usable) or now_s-self.last_plan > GAP_FAIL_S:
        self.state = self.FAILED
    elif stable and not engaged:
      self.state = self.ACTIVE
    return self.state == self.ACTIVE and plan_usable


def deliverable(query, ready, now):
  return 0 < query < ready <= now and ready-query <= MAX_LATENCY and now-query < MAX_PLAN_AGE


def reasoning_text(result):
  """The plan's reasoning text for the log, without the trajectory token (at most 512 characters)."""
  return str(result['prediction'].get('reasoning', '')).replace('<|traj_future_start|>', '').strip()[:512]


def packet(result):
  """Plan message fields, or None for startup results and plans too late to drive."""
  q,r,d = result['input']['query_ns'], result['output_ready_ns'], result['slot_deadline_ns']
  if result['startup'] or not deliverable(q,r,r):
    return None
  xyz = np.asarray(result['prediction']['xyz'])[0]
  rot = np.asarray(result['prediction']['rot'])[0]
  if result['trajectory_axes'] != 'forward/left/up' or not np.allclose(result['trajectory_times_s'], T[1:]):
    raise ValueError('Unsupported trajectory convention')
  return dict(queryMonoTime=result['input']['query_ns'], readyMonoTime=result['output_ready_ns'], slotDeadline=d,
              x=xyz[:, 0].tolist(), y=xyz[:, 1].tolist(), yaw=np.arctan2(rot[:, 1, 0], rot[:, 0, 0]).tolist(),
              reasoning=reasoning_text(result))


class PlanSelector:
  def __init__(self, straight_lookahead_s=LOOKAHEAD_S):
    # On a straight plan the near path mostly continues the current heading; the plan's correction toward the lane shows
    # farther ahead, so the lookahead grows to straight_lookahead_s as the plan's 3 s heading change falls below 0.05 rad.
    self.straight_lookahead_s = straight_lookahead_s
    self.query = self.ready = self.streak = 0
    self.curve = self.path = None
    self.odometry = deque()  # (ns, x, y, heading) of the vehicle; heading is the device yaw, left positive
    self.last_curvature = 0.
    self.tracker_status = {}  # outcome -> count, for the periodic modeld log

  def motion(self, ns, v_ego, heading):
    """Integrate vehicle odometry from speed and yaw (left positive). A constant yaw mounting offset rotates the whole
    odometry frame and cancels in the relative poses the tracker uses."""
    if not (np.isfinite(v_ego) and np.isfinite(heading)):
      return
    if self.odometry:
      t, x, y, h = self.odometry[-1]
      if ns == t:
        return
      dt = (ns-t)/1e9
      if not 0 < dt <= .5:
        self.odometry.clear()
      else:
        heading = h+(heading-h+math.pi) % (2*math.pi)-math.pi  # unwrap
        mid = (h+heading)/2
        self.odometry.append((ns, x+v_ego*math.cos(mid)*dt, y+v_ego*math.sin(mid)*dt, heading))
        while self.odometry and self.odometry[0][0] < ns-int(ODOMETRY_S*1e9):
          self.odometry.popleft()
        return
    self.odometry.append((ns, 0., 0., heading))

  def pose_at(self, ns):
    """Odometry pose at `ns`. After the newest sample, which modeld often reads 60-110 ms late, the last segment's
    motion is extrapolated for up to POSE_EXTRAPOLATION_NS."""
    if len(self.odometry) < 2 or not self.odometry[0][0] <= ns <= self.odometry[-1][0]+POSE_EXTRAPOLATION_NS:
      return None
    ts = [p[0] for p in self.odometry]
    i = min(max(int(np.searchsorted(ts, ns)), 1), len(ts)-1)
    a, b = self.odometry[i-1], self.odometry[i]
    f = (ns-a[0])/max(b[0]-a[0], 1)
    return tuple(a[k]+f*(b[k]-a[k]) for k in (1, 2, 3))

  def measured_curvature(self, now, v_ego):
    """Vehicle curvature from the odometry heading change over the last CURVATURE_WINDOW."""
    a, b = self.pose_at(now-int(CURVATURE_WINDOW*1e9)), self.pose_at(now)
    if a is None or b is None or v_ego < 1.:
      return 0.
    return (b[2]-a[2])/(v_ego*CURVATURE_WINDOW)

  def tracked_curvature(self, now, v_ego, lat_delay):
    """Pure pursuit on the newest plan's path, or None without odometry for it.
    The result is left positive, like the plan and the odometry."""
    query, current = self.pose_at(self.query), self.pose_at(now)
    if query is None or current is None or self.path is None:
      self.count('no query pose' if query is None else 'no current pose' if current is None else 'no path')
      return None
    x, y, _ = self.path
    qx, qy, qh = query
    wx, wy = qx+math.cos(qh)*x-math.sin(qh)*y, qy+math.sin(qh)*x+math.cos(qh)*y
    # Pose after the steering delay, with the measured curvature.
    px, py, ph = current
    d, k = v_ego*lat_delay, self.measured_curvature(now, v_ego)
    px, py, ph = px+d*math.cos(ph+k*d/2), py+d*math.sin(ph+k*d/2), ph+k*d
    fx = math.cos(ph)*(wx-px)+math.sin(ph)*(wy-py)
    fy = -math.sin(ph)*(wx-px)+math.cos(ph)*(wy-py)
    arc = np.concatenate(([0.], np.cumsum(np.hypot(np.diff(fx), np.diff(fy)))))
    age = (now-self.query)/1e9
    turn = abs(np.interp(age+3., T_PATH, self.path[2])-np.interp(age, T_PATH, self.path[2]))
    lookahead = float(np.interp(turn, (.05, .15), (self.straight_lookahead_s, LOOKAHEAD_S)))
    target = arc[int(np.argmin(np.hypot(fx, fy)))]+max(MIN_LOOKAHEAD, v_ego*lookahead)
    if target > arc[-1]:
      self.count('short path')
      return None
    tx, ty = np.interp(target, arc, fx), np.interp(target, arc, fy)
    self.count('tracked')
    return 2*ty/max(tx*tx+ty*ty, 1.)

  def count(self, outcome):
    self.tracker_status[outcome] = self.tracker_status.get(outcome, 0)+1

  def receive(self, plan, now, published=None):
    q, r = int(plan.queryMonoTime), int(plan.readyMonoTime)
    published = r if published is None else published
    if q <= self.query or not (r <= published <= now and deliverable(q,r,published) and now-published <= HANDOFF_GRACE):
      return  # An older, repeated, late or stale packet never replaces the current plan.
    if any(len(col) != 64 for col in (plan.x, plan.y, plan.yaw)):
      return
    x, y, yaw = np.array([[0., *col] for col in (plan.x, plan.y, plan.yaw)])
    if not np.isfinite([x, y, yaw]).all():
      return
    yaw = np.unwrap(yaw)
    speed = np.hypot(np.diff(x), np.diff(y)) / .1
    speed = np.interp(T, T[1:]-.05, speed)
    self.curve = yaw, speed, np.gradient(speed, .1), np.gradient(yaw, .1)
    self.path = x, y, yaw
    self.streak = self.streak+1 if 0 < q-self.query <= CONSECUTIVE_GAP else 1
    self.query, self.ready = q, r

  def candidate_action(self, now, v_ego, lat_delay, long_delay, v_ego_stopping):
    """Time-align the GPU plan without consulting any other model's path or action."""
    from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX
    from openpilot.selfdrive.controls.lib.drive_helpers import MAX_CURVATURE, MAX_LATERAL_ACCEL_NO_ROLL, get_accel_from_plan, get_curvature_from_plan
    if self.curve is None or self.streak < 2 or not self.ready <= now < self.query+MAX_PLAN_AGE:
      return None
    # Low speeds are valid: the curvature conversion clamps speed, and stops and starts need the plan's acceleration.
    if not np.isfinite(v_ego) or not (0. <= v_ego and 0 < lat_delay <= 2. and 0 < long_delay <= 2.):
      return None
    age = (now-self.query)/1e9
    yaw, speed, accel, yaw_rate = self.curve
    def sample(v):
      return np.interp(age+ACTION_TIMES, T, v)
    v = sample(speed)
    if abs(v[0]-v_ego) > 2.:
      return None
    theta = np.interp(age, T, yaw)
    curvature = get_curvature_from_plan(theta-sample(yaw), -sample(yaw_rate), ACTION_TIMES, v_ego, lat_delay)
    a, stop, _, desired_velocity = get_accel_from_plan(v, sample(accel), ACTION_TIMES, long_delay, v_ego_stopping)
    if (not np.isfinite([curvature,a]).all() or not ACCEL_MIN <= a <= ACCEL_MAX or
        abs(curvature) > MAX_CURVATURE or abs(curvature)*v_ego**2 > MAX_LATERAL_ACCEL_NO_ROLL):
      return None
    # The tracked command stays inside the same curvature and lateral-acceleration limits as the plan itself.
    limit = min(MAX_CURVATURE, MAX_LATERAL_ACCEL_NO_ROLL/max(v_ego, 1e-3)**2)
    tracked = self.tracked_curvature(now, v_ego, lat_delay)
    if tracked is not None:
      tracked = -tracked  # openpilot desiredCurvature is right positive, like the feedforward below
    if tracked is not None and np.isfinite(tracked):
      alpha = .05/(COMMAND_TAU+.05)
      tracked = self.last_curvature+alpha*(tracked-self.last_curvature)
    curvature = float(np.clip(tracked if tracked is not None and np.isfinite(tracked) else curvature, -limit, limit))
    self.last_curvature = curvature
    return dict(desiredCurvature=float(curvature), desiredAcceleration=float(a), desiredVelocity=float(desired_velocity), shouldStop=bool(stop))
