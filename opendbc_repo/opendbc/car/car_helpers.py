import os
import time
from urllib.parse import urlsplit

from opendbc.car import gen_empty_fingerprint
from opendbc.car.can_definitions import CanRecvCallable, CanSendCallable
from opendbc.car.carlog import carlog
from opendbc.car.structs import CarParams, CarParamsT
from opendbc.car.fingerprints import eliminate_incompatible_cars, all_legacy_fingerprint_cars
from opendbc.car.fw_versions import ObdCallback, get_fw_versions, get_fw_versions_ordered, get_present_ecus, match_fw_to_car
from opendbc.car.hyundai.fingerprints import FW_VERSIONS as HYUNDAI_FW_VERSIONS
from opendbc.car.hyundai.values import CAR as HYUNDAI
from opendbc.car.hyundai.values import CANFD_CAR, CANFD_UNSUPPORTED_LONGITUDINAL_CAR, HyundaiFlags
from opendbc.car.mock.values import CAR as MOCK
from opendbc.car.selected_car import get_selected_car_platform
from opendbc.car.values import BRANDS
from opendbc.car.vin import get_vin, is_valid_vin, VIN_UNKNOWN

from openpilot.common.params import Params


FRAME_FINGERPRINT = 100  # 1s


def format_git_source(remote: str | None, branch: str | None) -> str:
  remote = remote or ""
  # Normalize SCP-style SSH remotes as well as HTTPS/SSH URLs; never log credentials.
  if "://" not in remote:
    remote = "ssh://" + remote.replace(":", "/", 1)
  try:
    parsed = urlsplit(remote)
    parts = parsed.path.strip("/").split("/")
    owner = parts[0] if parsed.hostname and len(parts) >= 2 else "unknown"
  except ValueError:
    owner = "unknown"
  return f"{owner}/{branch or 'unknown'}"


def load_interfaces(brand_names):
  ret = {}
  for brand_name in brand_names:
    path = f'opendbc.car.{brand_name}'
    CarInterface = __import__(path + '.interface', fromlist=['CarInterface']).CarInterface
    for model_name in brand_names[brand_name]:
      ret[model_name] = CarInterface
  return ret


def _get_interface_names() -> dict[str, list[str]]:
  # returns a dict of brand name and its respective models
  brand_names = {}
  for brand in BRANDS:
    brand_name = brand.__module__.split('.')[-2]
    brand_names[brand_name] = [model.value for model in brand]

  return brand_names


# imports from directory opendbc/car/<name>/
interface_names = _get_interface_names()
interfaces = load_interfaces(interface_names)


def can_fingerprint(can_recv: CanRecvCallable) -> tuple[str | None, dict[int, dict]]:
  finger = gen_empty_fingerprint()
  candidate_cars = {i: all_legacy_fingerprint_cars() for i in [0, 1]}  # attempt fingerprint on both bus 0 and 1
  frame = 0
  car_fingerprint = None
  done = False

  while not done:
    # can_recv(wait_for_one=True) may return zero or multiple packets, so we increment frame for each one we receive
    can_packets = can_recv(wait_for_one=True)
    for can_packet in can_packets:
      for can in can_packet:
        # The fingerprint dict is generated for all buses, this way the car interface
        # can use it to detect a (valid) multipanda setup and initialize accordingly
        if can.src < 128:
          if can.src not in finger:
            finger[can.src] = {}
          finger[can.src][can.address] = len(can.dat)

        for b in candidate_cars:
          # Ignore extended messages and VIN query response.
          if can.src == b and can.address < 0x800 and can.address not in (0x7df, 0x7e0, 0x7e8):
            candidate_cars[b] = eliminate_incompatible_cars(can, candidate_cars[b])

      # if we only have one car choice and the time since we got our first
      # message has elapsed, exit
      for b in candidate_cars:
        if len(candidate_cars[b]) == 1 and frame > FRAME_FINGERPRINT:
          # fingerprint done
          car_fingerprint = candidate_cars[b][0]

      # bail if no cars left or we've been waiting for more than 2s
      failed = (all(len(cc) == 0 for cc in candidate_cars.values()) and frame > FRAME_FINGERPRINT) or frame > 200
      succeeded = car_fingerprint is not None
      done = failed or succeeded

      frame += 1

  return car_fingerprint, finger


def _ev6_fw_consistent(car_fw: list[CarParams.CarFw]) -> bool | None:
  # Only the identifying queries count here. HVAC, ADAS and date-only
  # responses are also collected, but do not identify the EV6 platform.
  expected = HYUNDAI_FW_VERSIONS[HYUNDAI.KIA_EV6]
  observed = {}
  for fw in car_fw:
    key = (fw.ecu.raw, fw.address, fw.subAddress or None)
    if fw.brand == "hyundai" and not fw.logging and key in expected:
      observed.setdefault(key, set()).add(fw.fwVersion)
  if not observed:
    return None
  return all(len(versions) == 1 and versions.issubset(expected[key]) for key, versions in observed.items())


# **** for use live only ****
def fingerprint(can_recv: CanRecvCallable, can_send: CanSendCallable, set_obd_multiplexing: ObdCallback, num_pandas: int,
                cached_params: CarParamsT | None, skip_fw_query: bool = False,
                verify_ev6: bool = False, auto_detect: bool = False) -> tuple[str | None, dict, str, list[CarParams.CarFw], CarParams.FingerprintSource, bool]:
  fixed_fingerprint = os.environ.get('FINGERPRINT', "")
  skip_fw_query = skip_fw_query or bool(fixed_fingerprint) or bool(os.environ.get('SKIP_FW_QUERY', False))
  disable_fw_cache = os.environ.get('DISABLE_FW_CACHE', False)
  ecu_rx_addrs = set()

  start_time = time.monotonic()
  if not skip_fw_query:
    if cached_params is not None and cached_params.brand != "mock" and len(cached_params.carFw) > 0 and \
       cached_params.carVin is not VIN_UNKNOWN and not disable_fw_cache:
      carlog.warning("Using cached CarParams")
      vin_rx_addr, vin_rx_bus, vin = -1, -1, cached_params.carVin
      car_fw = list(cached_params.carFw)
      cached = True
    else:
      carlog.warning("Getting VIN & FW versions")
      # enable OBD multiplexing for VIN query
      # NOTE: this takes ~0.1s and is relied on to allow sendcan subscriber to connect in time
      set_obd_multiplexing(True)
      # VIN query only reliably works through OBDII
      vin_rx_addr, vin_rx_bus, vin = get_vin(can_recv, can_send, (0, 1))
      ecu_rx_addrs = get_present_ecus(can_recv, can_send, set_obd_multiplexing, num_pandas=num_pandas)
      car_fw = get_fw_versions_ordered(can_recv, can_send, set_obd_multiplexing, vin, ecu_rx_addrs, num_pandas=num_pandas)
      cached = False

    exact_fw_match, fw_candidates = match_fw_to_car(car_fw, vin)
    if not cached and (verify_ev6 or (auto_detect and not fw_candidates)) and fw_candidates <= {HYUNDAI.KIA_EV6}:
      compatible = _ev6_fw_consistent(car_fw)
      adas_present = any(fw.brand == "hyundai" and fw.ecu == CarParams.Ecu.adas for fw in car_fw)
      # With no vehicle selected, only a known EV6 reply warrants another query.
      retry = compatible is True or (verify_ev6 and compatible is None)
      if retry and (not fw_candidates or not exact_fw_match or not adas_present):
        carlog.warning("EV6 firmware discovery incomplete; repeating the Hyundai query once")
        car_fw.extend(get_fw_versions(can_recv, can_send, set_obd_multiplexing, query_brand="hyundai", num_pandas=num_pandas))
        compatible = _ev6_fw_consistent(car_fw)
        exact_fw_match, fw_candidates = match_fw_to_car(car_fw, vin)
        if not verify_ev6 and (fw_candidates != {HYUNDAI.KIA_EV6} or not exact_fw_match or not compatible):
          fw_candidates = set()
      # The normal exact matcher accepts any listed version at an address.
      # Conflicting or unlisted replies cannot authorize verified EV6 control.
      if fw_candidates == {HYUNDAI.KIA_EV6} and not compatible:
        exact_fw_match = False
  else:
    carlog.warning("Skipping VIN & FW query")
    vin_rx_addr, vin_rx_bus, vin = -1, -1, VIN_UNKNOWN
    exact_fw_match, fw_candidates, car_fw = True, set(), []
    cached = False

  if not is_valid_vin(vin):
    carlog.error({"event": "Malformed VIN", "vin": vin})
    vin = VIN_UNKNOWN
  carlog.warning("VIN %s", vin)

  # disable OBD multiplexing for CAN fingerprinting and potential ECU knockouts
  set_obd_multiplexing(False)

  fw_query_time = time.monotonic() - start_time

  # CAN fingerprint
  # drain CAN socket so we get the latest messages
  can_recv()
  car_fingerprint, finger = can_fingerprint(can_recv)

  exact_match = True
  source = CarParams.FingerprintSource.can

  # If FW query returns exactly 1 candidate, use it
  if len(fw_candidates) == 1:
    car_fingerprint = list(fw_candidates)[0]
    source = CarParams.FingerprintSource.fw
    exact_match = exact_fw_match

  if fixed_fingerprint:
    car_fingerprint = fixed_fingerprint
    source = CarParams.FingerprintSource.fixed

  carlog.error({"event": "fingerprinted", "car_fingerprint": str(car_fingerprint), "source": source, "fuzzy": not exact_match,
                "cached": cached, "fw_count": len(car_fw), "ecu_responses": list(ecu_rx_addrs), "vin_rx_addr": vin_rx_addr,
                "vin_rx_bus": vin_rx_bus, "fingerprints": repr(finger), "fw_query_time": fw_query_time})

  return car_fingerprint, finger, vin, car_fw, source, exact_match


def get_car(can_recv: CanRecvCallable, can_send: CanSendCallable, set_obd_multiplexing: ObdCallback, alpha_long_allowed: bool,
            is_release: bool, num_pandas: int = 1, cached_params: CarParamsT | None = None):
  params = Params()
  selected_car = params.get("CarSelected3")
  automatic = selected_car == "AUTO"
  forced_candidate = get_selected_car_platform(selected_car) if selected_car and not automatic else None

  requested_platform = params.get("AutoExperimentalPlatform")
  # The web and Developer Alpha switch sets the legacy boolean. A manually
  # selected CAN-FD car on standard wiring still needs live firmware and CAN
  # identification before that request can grant longitudinal authority.
  verify_manual_alpha = (alpha_long_allowed and forced_candidate in CANFD_CAR and forced_candidate not in CANFD_UNSUPPORTED_LONGITUDINAL_CAR
                         and params.get_int("HyundaiCameraSCC") == 0)
  if verify_manual_alpha:
    alpha_long_allowed = (not requested_platform or requested_platform == forced_candidate) and not params.get_bool("IsReleaseBranch")
    if alpha_long_allowed:
      requested_platform = forced_candidate
  auto_setup = bool(requested_platform) and not params.get_bool("IsReleaseBranch") and (
    automatic or not selected_car or requested_platform == forced_candidate
  )
  # As on HKG, collect current firmware even with a manual EV6 HDA II selection.
  # Keep factory cruise ownership independent of the identification request.
  verify_stock_ev6 = (not auto_setup and not alpha_long_allowed and forced_candidate == HYUNDAI.KIA_EV6 and
                      selected_car == "Kia EV6 (with HDA II) 2022-24" and params.get_int("HyundaiCameraSCC") == 0 and
                      params.get_int("EnableRadarTracks") == 0)
  # A saved name or cached firmware cannot establish the current configuration
  # for a new longitudinal controller. Keep the existing manual fast path otherwise.
  candidate, fingerprints, vin, car_fw, source, exact_match = fingerprint(
    can_recv, can_send, set_obd_multiplexing, num_pandas, None if auto_setup or automatic or verify_stock_ev6 else cached_params,
    skip_fw_query=forced_candidate is not None and not (auto_setup or verify_stock_ev6),
    auto_detect=automatic and not auto_setup,
    verify_ev6=verify_stock_ev6 or (auto_setup and requested_platform == HYUNDAI.KIA_EV6 and params.get_int("HyundaiCameraSCC") == 0))

  # Automatic selection never borrows a previous vehicle's Alpha request.
  # Keep the detected identity for the UI even if longitudinal verification fails.
  detected = candidate if source != CarParams.FingerprintSource.fixed else None
  if automatic:
    alpha_long_allowed = False
    candidate = detected
  if auto_setup:
    standard_canfd = requested_platform in CANFD_CAR and params.get_int("HyundaiCameraSCC") == 0
    if (not exact_match or source == CarParams.FingerprintSource.fixed or candidate != requested_platform or
        (standard_canfd and source != CarParams.FingerprintSource.fw)):
      params.put("AutoExperimentalIssue", "identity")
      candidate = None
    alpha_long_allowed = candidate == requested_platform
  elif forced_candidate is not None:
    if verify_stock_ev6 and ((candidate is not None and candidate != forced_candidate) or _ev6_fw_consistent(car_fw) is False):
      params.put("AutoExperimentalIssue", "identity")
      candidate = None
    elif not (verify_stock_ev6 and candidate == forced_candidate and source == CarParams.FingerprintSource.fw and exact_match):
      candidate = forced_candidate
      source = CarParams.FingerprintSource.fixed
      exact_match = True
      if verify_stock_ev6:
        car_fw = []  # Unconfirmed firmware cannot change the manual stock configuration.

  if candidate is None:
    carlog.error({"event": "car doesn't match any fingerprints", "fingerprints": repr(fingerprints)})
    candidate = "MOCK"

  print(f"SelectedCar = {candidate}")
  params.put("CarName", str(candidate))

  params.put("FingerPrints", str(fingerprints))
  CarInterface = interfaces[candidate]
  CP: CarParams = CarInterface.get_params(candidate, fingerprints, car_fw, alpha_long_allowed, is_release, docs=False)
  if (auto_setup and CP.brand == "hyundai" and CP.flags & HyundaiFlags.CANFD_HDA2 and params.get_int("HyundaiCameraSCC") == 0
      and candidate not in CANFD_UNSUPPORTED_LONGITUDINAL_CAR and not CP.alphaLongitudinalAvailable):
    params.put("AutoExperimentalIssue", "adas")
  verify_wiring = (auto_setup or automatic) and CP.brand == "hyundai" and (CP.openpilotLongitudinalControl or params.get_int("HyundaiCameraSCC") == 3)
  verified_stock_adas = (verify_stock_ev6 and CP.brand == "hyundai" and source == CarParams.FingerprintSource.fw and
                         any(fw.ecu == CarParams.Ecu.adas for fw in car_fw))
  if (verify_wiring or verified_stock_adas) and not CarInterface.auto_longitudinal_bus_valid(CP, fingerprints, car_fw):
    carlog.warning("CAN fingerprint does not confirm the selected longitudinal wiring; using observation only")
    params.put("AutoExperimentalIssue", "wiring")
    candidate = MOCK.MOCK
    CP = interfaces[candidate].get_params(candidate, fingerprints, car_fw, False, is_release, docs=False)
    params.put("CarName", str(candidate))
  if automatic:
    params.put("AutoCarModelResult", str(detected) if detected else "unknown")
  CP.carVin = vin
  CP.carFw = car_fw
  CP.fingerprintSource = source
  CP.fuzzyFingerprint = not exact_match

  print("Carrot GitBranch = {}, {}".format(format_git_source(params.get("GitRemote"), params.get("GitBranch")),
                                         params.get("GitCommitDate")))

  return interfaces[CP.carFingerprint](CP)


def get_demo_car_params():
  platform = MOCK.MOCK
  CarInterface = interfaces[platform]
  CP = CarInterface.get_non_essential_params(platform)
  return CP
