"""Decode real rlogs/HEVC, calibrated N16 features and measured Edge histories."""
from collections import defaultdict, deque
from pathlib import Path
from types import SimpleNamespace
import math
import time

from tools.training_studio.head import ACTION, CONTEXT, FEATURES, instrument
from tools.training_studio import plan_head
from tools.training_studio.store import read_json, write_json


def nearest(rows, timestamp, tolerance):
  import bisect
  if not rows:
    raise ValueError("required logged service missing")
  index = bisect.bisect_left([row[0] for row in rows], timestamp)
  candidates = rows[max(0,index-1):index+1]
  row = min(candidates, key=lambda value:abs(value[0]-timestamp))
  if abs(row[0]-timestamp) > tolerance:
    raise ValueError("logged service timestamp outside tolerance")
  return row[1]


def previous(rows, timestamp, tolerance):
  import bisect
  index = bisect.bisect_right([row[0] for row in rows], timestamp)-1
  if index < 0 or timestamp-rows[index][0] > tolerance:
    raise ValueError("missing or stale causal log input")
  return rows[index][1]


def preprocess(images, intrinsics, calibration):
  import numpy as np
  from openpilot.common.transformations.model import get_warp_matrix
  def indices(matrix,width,height,source_width,source_height):
    x,y=np.meshgrid(np.arange(width,dtype=np.float32),np.arange(height,dtype=np.float32))
    values=matrix@np.stack((x.ravel(),y.ravel(),np.ones(x.size,np.float32)))
    sx=np.rint(values[0]/values[2]).astype(np.int64).clip(0,source_width-1)
    sy=np.rint(values[1]/values[2]).astype(np.int64).clip(0,source_height-1)
    return sy.reshape(height,width),sx.reshape(height,width)
  prepared = []
  for image, camera, wide in zip(images, intrinsics, (False,True), strict=True):
    height,width = image.shape[:2]
    matrix = get_warp_matrix(np.asarray(calibration,np.float32), camera, wide).astype(np.float32)
    uv_matrix = matrix * np.array([[1,1,.5],[1,1,.5],[2,2,1]],np.float32)
    ymap, uvmap = indices(matrix,512,256,width,height), indices(uv_matrix,256,128,width//2,height//2)
    r,g,b = (image[:,:,i].astype(np.int32) for i in range(3))
    y = np.clip(((b*13+g*65+r*33+64)>>7)+16,0,255).astype(np.uint8)
    r,g,b = ((v[::2,::2]+v[::2,1::2]+v[1::2,::2]+v[1::2,1::2]+2)>>2 for v in (r,g,b))
    u = np.clip((b*56-g*37-r*19+0x8080)>>8,0,255).astype(np.uint8)
    v = np.clip((r*56-g*47-b*9+0x8080)>>8,0,255).astype(np.uint8)
    y,u,v = y[ymap],u[uvmap],v[uvmap]
    prepared.append(np.stack((y[::2,::2],y[1::2,::2],y[::2,1::2],y[1::2,1::2],u,v)))
  return np.stack(prepared)


def log_events(path, schema_checkout=None):
  """Use the recording branch's schema, isolated from other loaded Cap'n Proto schemas."""
  import bz2
  import capnp
  import zstandard
  root=Path(schema_checkout).resolve() if schema_checkout else Path(__file__).resolve().parents[2]
  cereal=root/"openpilot/cereal"
  dbc=root/"opendbc_repo/opendbc/car"
  parser=capnp.SchemaParser()
  # pycapnp can abort the interpreter resolving absolute imports in non-ASCII roots.
  if str(root).isascii():
    schema=parser.load(str(cereal/"log.capnp"),imports=[str(cereal),str(dbc)])
  else:
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
      roots=[]
      for index, source in enumerate((cereal,dbc)):
        dest=Path(temp)/str(index)
        (dest/"include").mkdir(parents=True)
        for item in (*source.glob("*.capnp"), *source.glob("include/*.capnp")):
          shutil.copyfile(item,dest/item.relative_to(source))
        roots.append(str(dest))
      schema=parser.load(str(Path(roots[0])/"log.capnp"),imports=roots)
  if path.stat().st_size>64*1024**2:
    raise ValueError("rlog exceeds offline decoder input budget")
  data=path.read_bytes()
  limit=256*1024**2
  if data.startswith(b"BZh"):
    decoder=bz2.BZ2Decompressor()
    data=decoder.decompress(data,max_length=limit+1)
    if not decoder.eof:
      raise ValueError("truncated or oversized decompressed rlog")
  elif path.suffix==".zst":
    with zstandard.ZstdDecompressor().stream_reader(data) as reader:
      data=reader.read(limit+1)
  if len(data)>limit:
    raise ValueError("decompressed rlog exceeds offline decoder budget")
  yield from schema.Event.read_multiple_bytes(data)


def front_route(instruction, age, speed):
  """Match the car's navigation-vector mode with an unavailable map raster."""
  import numpy as np
  from openpilot.selfdrive.navigation.commands import navigation_input
  direction = "follow"
  vector = np.zeros(47, np.float32)
  moves = instruction.get("allManeuvers", [])
  if moves or instruction.get("maneuverType") not in (None, "", "invalid") or instruction.get("maneuverModifier"):
    if not moves or not 0 <= age < 2 or not math.isfinite(speed):
      raise ValueError("missing or stale recorded maneuver")
    move = moves[0]
    kind, direction = move.get("type"), move.get("modifier")
    if (kind not in ("turn","continue","end of road","new name") or direction not in ("left","right","straight")
        or instruction.get("maneuverType") != kind or instruction.get("maneuverModifier") != direction):
      raise ValueError("unsupported or inconsistent next maneuver")
    distance = move.get("distance")
    if not isinstance(distance,(float,int)) or not math.isfinite(distance):
      raise ValueError("invalid maneuver distance")
    vector = navigation_input([SimpleNamespace(type=kind,modifier=direction,distance=distance)], max(0.,speed)*age)
    if not vector[:-1].any():
      raise ValueError("recorded maneuver has expired")
  intent = "Follow the current lane." if direction == "follow" else f"At the indicated junction in {vector[-1]*100:.0f} meters, go {direction}."
  prompt = (intent + " Obey the applicable traffic light. Yield to oncoming traffic and pedestrians before turning. "
            "Stay centered within the intended lane. Side and rear views are unavailable; do not assume an occluded path is clear.")
  return vector, direction, prompt


def measured_pose_rows(services):
  """Support legacy ECEF and modern livePose measured dead reckoning over short histories."""
  import numpy as np
  from openpilot.common.transformations.orientation import rot_from_euler
  legacy=services["liveLocationKalman"]
  if legacy:
    return legacy
  position=np.zeros(3,np.float64)
  previous_time=None
  previous_velocity=None
  rows=[]
  for timestamp,pose in sorted(services["livePose"]):
    if not all(pose.get(key) for key in ("inputsOK","sensorsOK","posenetOK")):
      previous_time=None
      previous_velocity=None
      continue
    orientation,velocity=pose["orientationNED"],pose["velocityDevice"]
    if not orientation.get("valid") or not velocity.get("valid"):
      continue
    rotation=rot_from_euler([orientation[key] for key in ("x","y","z")])
    velocity_ned=rotation@np.array([velocity[key] for key in ("x","y","z")])
    if previous_time is not None:
      dt=timestamp-previous_time
      if not 0<dt<=.15:
        previous_time=None
        previous_velocity=None
        continue
      position+=(velocity_ned+previous_velocity)*.5*dt
    try:
      calibration=previous(services["extrinsicsCalibration"] or services["liveCalibration"],timestamp,120)
    except ValueError:
      previous_time=None
      previous_velocity=None
      continue
    if calibration.get("calStatus") not in ("calibrated",1):
      previous_time=None
      previous_velocity=None
      continue
    calibrated=rotation@rot_from_euler(calibration["rpyCalib"])
    rows.append((timestamp,{"status":"valid","positionECEF":{"valid":True,"value":position.copy()},
      "orientationECEF":{"valid":True,"value":[orientation[key] for key in ("x","y","z")]},
      "measured_rotation":calibrated,"short_history_dead_reckoning":True}))
    previous_time,previous_velocity=timestamp,velocity_ned
  return rows


def prepare(folder):
  import numpy as np
  import onnxruntime as ort
  from PIL import Image
  from openpilot.tools.lib.framereader import FrameReader
  from openpilot.common.transformations.camera import DEVICE_CAMERAS
  from openpilot.common.transformations.orientation import rot_from_euler
  folder = Path(folder)
  plan = read_json(folder / "plan.json")
  instrument(folder / "source.onnx", folder / "features.onnx")
  options = ort.SessionOptions()
  options.intra_op_num_threads = 4
  options.log_severity_level = 3
  providers = [plan["config"].get("feature_provider", "CPUExecutionProvider")]
  session = ort.InferenceSession(str(folder / "features.onnx"), sess_options=options, providers=providers)
  if providers[0] not in session.get_providers():
    raise RuntimeError("requested N16 feature backend unavailable")
  types = {"tensor(float)":np.float32,"tensor(float16)":np.float16,"tensor(uint8)":np.uint8}
  inputs = {value.name:np.zeros(value.shape,types[value.type]) for value in session.get_inputs()}
  output_names = [value.name for value in session.get_outputs()]
  state_pairs = {name:"next_"+name for name in inputs if "next_"+name in output_names}
  packets = folder / "packets"
  packets.mkdir()
  rows, rejected = [], defaultdict(int)
  cadence = float(plan["config"].get("sample_interval_s", 1.0))
  for dataset in plan["datasets"]:
    path = Path(dataset["path"])
    rlog = next(path/name for name in ("rlog.zst","rlog.bz2","rlog") if (path/name).is_file())
    services = defaultdict(list)
    wanted = {"narrowRoadEncodeIdx","roadEncodeIdx","wideRoadEncodeIdx","liveLocationKalman","livePose","carState","deviceState",
      "narrowRoadCameraState","roadCameraState","extrinsicsCalibration","liveCalibration","modelV2","navInstruction","navInstructionCarrot"}
    for event in log_events(rlog,plan["config"].get("schema_checkout")):
      try:
        kind = event.which()
        if kind == "navInstructionCarrot":
          services[kind].append((event.logMonoTime*1e-9, getattr(event,kind).to_dict() if event.valid else None))
        elif kind in wanted and event.valid:
          services[kind].append((event.logMonoTime*1e-9, getattr(event,kind).to_dict()))
      except (ValueError,AttributeError):
        continue
    narrow = sorted(services["narrowRoadEncodeIdx"] or services["roadEncodeIdx"])
    wide = sorted(services["wideRoadEncodeIdx"])
    services["poses"]=measured_pose_rows(services)
    # Encode indices identify the exact frames within each uploaded segment.
    cameras = (FrameReader(str(path/"fcamera.hevc"),hwaccel="none"),FrameReader(str(path/"ecamera.hevc"),hwaccel="none"))
    if any((camera.w,camera.h) not in ((1928,1208),(1344,760)) for camera in cameras):
      raise ValueError("unsupported recorded camera dimensions")
    for value in inputs.values():
      value[:] = 0
    inputs["traffic_convention"][:] = [[1,0]]
    inputs["action_t"][:] = [[.2,.3]]
    history = deque(maxlen=50)
    last_sample = -1e9
    last_frame_time=None
    for _, index in narrow:
      timestamp = index.get("timestampSof",0)*1e-9
      inferred=False
      try:
        if not timestamp:
          raise ValueError("camera timestamp missing")
        if last_frame_time is not None and not 0<timestamp-last_frame_time<=.075:
          history.clear()
          for name in state_pairs:
            inputs[name][:]=0
        _, wide_index = min(wide, key=lambda row:abs(row[1].get("timestampSof",0)*1e-9-timestamp))
        wide_time = wide_index.get("timestampSof",0)*1e-9
        if abs(wide_time-timestamp) > .015:
          raise ValueError("front cameras not synchronized")
        image_ids = [index["segmentId"],wide_index["segmentId"]]
        images = [camera.get(frame) for camera,frame in zip(cameras,image_ids,strict=True)]
        state = previous(services["carState"],timestamp,.15)
        device = previous(services["deviceState"],timestamp,120).get("deviceType","unknown")
        camera_state = previous(services["narrowRoadCameraState"] or services["roadCameraState"],timestamp,.15)
        geometry = DEVICE_CAMERAS[(device,camera_state.get("sensor","unknown"))]
        if any((image.shape[1],image.shape[0]) != camera.size for image,camera in zip(images,(geometry.narrow_road,geometry.wide_road),strict=True)):
          raise ValueError("logged camera geometry mismatch")
        calibration = previous(services["extrinsicsCalibration"] or services["liveCalibration"],timestamp,120)
        if calibration.get("calStatus") not in ("calibrated",1):
          raise ValueError("camera calibration unavailable")
        pose = previous(services["poses"],timestamp,.1)
        if pose.get("status") != "valid" or not pose["positionECEF"]["valid"] or not pose["orientationECEF"]["valid"]:
          raise ValueError("valid measured ego pose required")
        position = np.asarray(pose["positionECEF"]["value"],np.float64)
        attitude = pose.get("calibratedOrientationECEF",pose["orientationECEF"])
        if not attitude["valid"]:
          raise ValueError("calibrated ego orientation unavailable")
        rotation = pose["measured_rotation"] if "measured_rotation" in pose else rot_from_euler(attitude["value"])
        # Preserve actual capture times and field of view; only reduce pixel count for the teacher transport.
        teacher_images = []
        for image in reversed(images):
          height,width = image.shape[:2]
          target = (min(width,1024),round(height*min(width,1024)/width))
          teacher_images.append(np.asarray(Image.fromarray(image).resize(target,Image.Resampling.BICUBIC)).transpose(2,0,1))
        history.append({"time":timestamp,"wide_time":wide_time,"images":np.stack(teacher_images),"position":position,"rotation":rotation})
        inputs["new_img"][:] = preprocess(images,(geometry.narrow_road.intrinsics,geometry.wide_road.intrinsics),calibration["rpyCalib"])
        # Replay the car's navigation-vector input. Uploaded recordings have no IPC map raster.
        inputs["navigation"][:] = 0
        inputs["nav_map"][:] = 0
        routed = plan["config"].get("navigation_training") == "recorded_front_route"
        direction = "follow"
        prompt = "Follow the current lane. Obey traffic signals and yield to visible hazards. Side and rear views are unavailable."
        if routed:
          from bisect import bisect_right
          nav_rows = services["navInstructionCarrot"]
          nav_i = bisect_right(nav_rows,timestamp,key=lambda row:row[0])-1
          instruction = {}
          age = 0.
          if nav_i >= 0:
            nav_time,note = nav_rows[nav_i]
            age = timestamp-nav_time
            instruction = note or {}
          if not instruction:
            legacy_rows = services["navInstruction"]
            legacy_i = bisect_right(legacy_rows,timestamp,key=lambda row:row[0])-1
            legacy = legacy_rows[legacy_i][1] if legacy_i >= 0 and timestamp-legacy_rows[legacy_i][0] < 2 else {}
            if legacy.get("allManeuvers") or legacy.get("maneuverType") not in (None,"","invalid"):
              raise ValueError("route missing model-facing Carrot instruction")
          inputs["navigation"][:],direction,prompt = front_route(instruction,age,state["vEgo"])
        result = dict(zip(output_names, session.run(None,inputs),strict=True))
        for name,next_name in state_pairs.items():
          inputs[name] = result[next_name]
        last_frame_time=timestamp
        inferred=True
        if len(history)<40 or timestamp-last_sample<cadence:
          continue
        if state.get("leftBlinker") or state.get("rightBlinker") or state.get("leftBlindspot") or state.get("rightBlindspot"):
          raise ValueError("side-gap-dependent maneuver excluded")
        if services["modelV2"] or direction != "follow":
          prediction = previous(services["modelV2"],timestamp,.3)
          meta = prediction.get("meta",{})
          if (meta.get("laneChangeState") not in ("off",0) or meta.get("desire") in ("laneChangeLeft","laneChangeRight",3,4)
              or meta.get("autoTurnSignalLaneChange")):
            raise ValueError("lane change excluded")
        if not routed and (services["navInstruction"] or services["navInstructionCarrot"]):
          navigation = previous(services["navInstructionCarrot"] or services["navInstruction"],timestamp,2)
          if navigation and (navigation.get("maneuverType") or navigation.get("maneuverModifier")):
            raise ValueError("routed samples require recorded N16 map inputs; withheld")
        frame_rows = [min(history,key=lambda row:abs(row["time"]-(timestamp+offset))) for offset in (-2,-1,-.5,-.1,0)]
        if any(abs(row["time"]-(timestamp+offset))>.035 for row,offset in zip(frame_rows,(-2,-1,-.5,-.1,0),strict=True)):
          raise ValueError("teacher image history has gaps")
        poses = [min(history,key=lambda row:abs(row["time"]-(timestamp+offset))) for offset in np.arange(-19,1)*.1]
        if any(abs(row["time"]-(timestamp+offset))>.035 for row,offset in zip(poses,np.arange(-19,1)*.1,strict=True)):
          raise ValueError("ego history has gaps")
        reference = history[-1]
        identifier = f"{len(rows):08d}"
        axis = np.diag([1.,-1.,-1.])  # openpilot FRD -> teacher FLU, a proper rotation
        packet = {"image_frames":np.stack([row["images"] for row in frame_rows],axis=1).reshape(10,1,3,*frame_rows[0]["images"].shape[-2:]),
          "camera_indices":np.repeat(np.array([1,6],np.int64),5),
          "absolute_timestamps":np.array([round(row[key]*1e6) for key in ("wide_time","time") for row in frame_rows],np.int64),
          "ego_history_timestamps":np.array([round(row["time"]*1e6) for row in poses],np.int64),
          "ego_history_xyz":((np.stack([row["position"] for row in poses])-reference["position"])@reference["rotation"]@axis)[None,None].astype(np.float32),
          "ego_history_rot":(axis@reference["rotation"].T@np.stack([row["rotation"] for row in poses])@axis)[None,None].astype(np.float32),
          "nav_text":np.array(prompt)}
        np.savez_compressed(packets/(identifier+".npz"),**packet)
        rows.append({"id":identifier,"split":dataset["split"],"group":dataset["route_group"],"speed":state["vEgo"],
          "maneuver":direction,"features":result[FEATURES][0].tolist(),"context":result[CONTEXT][0].tolist(),"source_action":result[ACTION][0].tolist(),
          "plan_features":result[plan_head.FEATURES][0].tolist()})
        last_sample = timestamp
        write_json(folder/"progress.json",{"stage":"prepare","samples":len(rows),"rejected":dict(rejected),"updated":time.time()})
      except (ValueError,KeyError,IndexError) as exc:
        rejected[str(exc)] += 1
        # Any missing recurrent frame invalidates its context; warm up again.
        if not inferred:
          history.clear()
          last_frame_time=None
          for name in state_pairs:
            inputs[name][:]=0
    write_json(folder/"prepared.json",{"samples":rows,"rejected":dict(rejected),"navigation_mode":plan["config"].get("navigation_training","no_route_only"),"feature_provider":providers[0]})
  if not rows:
    raise ValueError("no qualified observed samples; inspect prepared.json rejection counts")
