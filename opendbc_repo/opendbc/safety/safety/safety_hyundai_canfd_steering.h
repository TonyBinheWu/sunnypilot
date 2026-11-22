#pragma once

// Redundant CAN buses need independent histories/request-cut counters.
typedef struct {
  int desired;
  int rt;
  int valid_requests;
  int invalid_requests;
  uint32_t rt_ts;
  uint32_t cut_ts;
} HyundaiCanfdSteerHistory;

static HyundaiCanfdSteerHistory hyundai_canfd_aux_steering[3];
static HyundaiCanfdSteerHistory hyundai_canfd_forward_steering[3];
static bool hyundai_canfd_always_lateral = false;
static bool hyundai_canfd_angle_control = false;
static uint32_t hyundai_canfd_wheel_max = 0U;
static uint32_t hyundai_canfd_wheel_min = 0U;
static bool hyundai_canfd_wheel_reverse = false;
typedef struct {
  uint32_t fields;
  uint16_t angle;
  uint32_t ts;
  bool seen;
} HyundaiCanfdStockAngle;
static HyundaiCanfdStockAngle hyundai_canfd_stock_angle[4];

static int hyundai_canfd_angle_index(int addr) {
  return (addr == 0x12A) ? 0 : (addr == 0xCB) ? 1 : (addr == 0x50) ? 2 : (addr == 0x110) ? 3 : -1;
}

static HyundaiCanfdStockAngle hyundai_canfd_angle_fields(const CANPacket_t *msg) {
  const bool alt = GET_ADDR(msg) == 0xCB;
  const uint32_t active = alt ? ((GET_BYTE(msg, 3) >> 4U) & 3U) : ((GET_BYTE(msg, 9) >> 4U) & 3U);
  const uint32_t authority = alt ? GET_BYTE(msg, 6) : GET_BYTE(msg, 12);
  const uint32_t torque = alt ? 0U : (((GET_BYTE(msg, 6) & 0x1FU) << 7U) | (GET_BYTE(msg, 5) >> 1U));
  const uint32_t mode = alt ? 0U : (GET_BYTE(msg, 3) & 0x1FU);
  const uint16_t angle = alt ? (GET_BYTES(msg, 4, 2) & 0x3FFFU) : ((GET_BYTES(msg, 10, 2) >> 2U) & 0x3FFFU);
  return (HyundaiCanfdStockAngle){.fields = torque | (mode << 12U) | (active << 17U) | (authority << 19U),
    .angle = angle, .ts = microsecond_timer_get(), .seen = true};
}

static void hyundai_canfd_stock_angle_rx(const CANPacket_t *msg) {
  const int addr = GET_ADDR(msg);
  const int i = hyundai_canfd_angle_index(addr);
  const int length = (addr == 0xCB) ? 24 : (addr == 0x110) ? 32 : 16;
  if (hyundai_canfd_angle_control && (GET_BUS(msg) == 2) && (i >= 0) && (GET_LEN(msg) == length) &&
      (hyundai_canfd_get_checksum(msg) == hyundai_common_canfd_compute_checksum(msg))) {
    hyundai_canfd_stock_angle[i] = hyundai_canfd_angle_fields(msg);
  }
}

static bool hyundai_canfd_matches_stock_angle(const CANPacket_t *msg) {
  const int i = hyundai_canfd_angle_index(GET_ADDR(msg));
  const HyundaiCanfdStockAngle current = hyundai_canfd_angle_fields(msg);
  return (i >= 0) && hyundai_canfd_stock_angle[i].seen &&
    (get_ts_elapsed(current.ts, hyundai_canfd_stock_angle[i].ts) <= 100000U) &&
    (current.fields == hyundai_canfd_stock_angle[i].fields) && (current.angle == hyundai_canfd_stock_angle[i].angle);
}

static HyundaiCanfdSteerHistory hyundai_canfd_steer_capture(void) {
  return (HyundaiCanfdSteerHistory){desired_torque_last, rt_torque_last, valid_steer_req_count,
    invalid_steer_req_count, ts_torque_check_last, ts_steer_req_mismatch_last};
}

static void hyundai_canfd_steer_restore(HyundaiCanfdSteerHistory state) {
  desired_torque_last = state.desired;
  rt_torque_last = state.rt;
  valid_steer_req_count = state.valid_requests;
  invalid_steer_req_count = state.invalid_requests;
  ts_torque_check_last = state.rt_ts;
  ts_steer_req_mismatch_last = state.cut_ts;
}

static void hyundai_canfd_steer_reset(uint16_t param) {
  hyundai_canfd_always_lateral = GET_FLAG(param, 1024);
  hyundai_canfd_angle_control = GET_FLAG(param, 32768);
  hyundai_canfd_wheel_max = 0U;
  hyundai_canfd_wheel_min = 0U;
  hyundai_canfd_wheel_reverse = false;
  for (unsigned int i = 0U; i < 4U; i++) {
    hyundai_canfd_stock_angle[i] = (HyundaiCanfdStockAngle){0};
  }
  for (unsigned int i = 0U; i < 3U; i++) {
    hyundai_canfd_aux_steering[i] = (HyundaiCanfdSteerHistory){0};
    hyundai_canfd_forward_steering[i] = (HyundaiCanfdSteerHistory){0};
  }
}

static bool hyundai_canfd_steering_tx_check(const CANPacket_t *msg) {
  const int addr = GET_ADDR(msg);
  const int bus = GET_BUS(msg);
  const bool lfa = addr == 0x12A;
  const bool lfa_alt = addr == 0xCB;
  if (!lfa && !lfa_alt && (addr != 0x50) && (addr != 0x110)) {
    return false;
  }
  const int ecan = (hyundai_canfd_hda2 && !hyundai_camera_scc) ? 1 : 0;
  const int acan = 1 - ecan;
  const int primary_bus = (hyundai_canfd_hda2 && !hyundai_camera_scc && !hyundai_longitudinal) ? acan : ecan;
  const int expected_len = lfa_alt ? 24 : ((addr == 0x110) ? 32 : 16);
  const bool route_ok = (lfa || lfa_alt) ? (bus == ecan) :
    (hyundai_canfd_hda2 && (bus == acan) && (addr == hyundai_canfd_hda2_get_lkas_addr()));
  if (!route_ok || (GET_LEN(msg) != expected_len) ||
      (hyundai_canfd_get_checksum(msg) != hyundai_common_canfd_compute_checksum(msg))) {
    return true;
  }

  const uint32_t now = microsecond_timer_get();
  const bool fresh = hyundai_rx_fresh_on_bus(0xA0, ecan, now) && hyundai_rx_fresh_on_bus(0xEA, ecan, now);
  // Explicit Always Lateral authorization; do not inherit unconditional AOL
  // admission from the fork's shared torque helper on every configuration.
  const bool allowed = controls_allowed || (hyundai_canfd_always_lateral && fresh);
  const int angle_active = lfa_alt ? ((GET_BYTE(msg, 3) >> 4U) & 3U) : ((GET_BYTE(msg, 9) >> 4U) & 3U);
  if (lfa_alt || (angle_active != 0)) {
    // Angle authority is not increased by this torque-only feature.
    if (!hyundai_canfd_angle_control) {
      return true;
    }
    const int authority = lfa_alt ? GET_BYTE(msg, 6) : GET_BYTE(msg, 12);
    const bool active = angle_active >= 2;
    const bool violation = (authority > 250) || (active && !allowed) || (!active && (authority != 0));
    // The controller's OEM emergency passthrough may reproduce an original
    // command. Only fresh, CRC-verified control fields from physical CAM may
    // authorize it; the host cannot invent an exception.
    return violation && !hyundai_canfd_matches_stock_angle(msg);
  }

  const int desired = (((GET_BYTE(msg, 6) & 0xFU) << 7U) | (GET_BYTE(msg, 5) >> 1U)) - 1024U;
  const bool request = GET_BIT(msg, 52U);
  if (hyundai_canfd_angle_control && lfa && (desired == -1024) && !request &&
      ((GET_BYTE(msg, 3) & 7U) == 0U) && (GET_BYTE(msg, 12) == 0U)) {
    return false;  // Existing CAMERA_SCC angle mode's disabled legacy LFA sentinel.
  }
  int rate_up = 2;
  // This safety parameter is the REQUIRED withdrawal under driver override,
  // not a normal maximum decrease. Keep it at the factory value so cancelling
  // host headroom (which restores 2/3) never conflicts with driver takeover.
  const int rate_down = 3;
  // Fastest wheel, correct physical bus, valid CRC/counter, <=100 ms old.
  // Raw wheel speed: 1/32 km/h. Never trust host-provided speed for this bound.
  if (fresh && !hyundai_canfd_angle_control && !hyundai_canfd_wheel_reverse &&
      (torque_driver.min >= -250) && (torque_driver.max <= 250) && (hyundai_canfd_wheel_min >= 35U) &&
      (hyundai_canfd_wheel_max < 1280U) && ((hyundai_canfd_wheel_max - hyundai_canfd_wheel_min) <= 96U)) {
    const uint32_t remaining = MIN(1280U - hyundai_canfd_wheel_max, 320U);
    rate_up += (int)((2U * remaining + 319U) / 320U);
  }
  const TorqueSteeringLimits limits = {
    .max_steer = 512, .max_rate_up = rate_up, .max_rate_down = rate_down,
    .max_rt_delta = 112, .max_rt_interval = 250000U,
    .driver_torque_allowance = 250, .driver_torque_multiplier = 2, .type = TorqueDriverLimited,
    .min_valid_request_frames = 89, .max_invalid_request_frames = 2,
    .min_valid_request_rt_interval = 810000U, .has_steer_req_tolerance = true,
  };
  const HyundaiCanfdSteerHistory primary = hyundai_canfd_steer_capture();
  const bool auxiliary = bus != primary_bus;
  if (auxiliary) {
    hyundai_canfd_steer_restore(hyundai_canfd_aux_steering[bus]);
  }
  bool violation = steer_torque_cmd_checks(desired, request, limits);
  violation |= !allowed && (desired != 0);
  if (violation) {
    hyundai_canfd_steer_restore((HyundaiCanfdSteerHistory){.rt_ts = now, .cut_ts = now});
  }
  if (auxiliary) {
    hyundai_canfd_aux_steering[bus] = hyundai_canfd_steer_capture();
    hyundai_canfd_steer_restore(primary);
  }
  return violation;
}

// RX-paced replacement/reuse is a second transmission path. Revalidate its
// actual output history, not just the host's enqueue history.
static bool hyundai_canfd_steering_forward_check(const CANPacket_t *msg) {
  const int bus = GET_BUS(msg);
  const int ecan = (hyundai_canfd_hda2 && !hyundai_camera_scc) ? 1 : 0;
  const int primary_bus = (hyundai_canfd_hda2 && !hyundai_camera_scc && !hyundai_longitudinal) ? (1 - ecan) : ecan;
  const HyundaiCanfdSteerHistory primary = hyundai_canfd_steer_capture();
  const HyundaiCanfdSteerHistory auxiliary = hyundai_canfd_aux_steering[bus];
  hyundai_canfd_steer_restore(hyundai_canfd_forward_steering[bus]);
  hyundai_canfd_aux_steering[bus] = hyundai_canfd_forward_steering[bus];
  const bool violation = hyundai_canfd_steering_tx_check(msg);
  hyundai_canfd_forward_steering[bus] = (bus == primary_bus) ? hyundai_canfd_steer_capture() : hyundai_canfd_aux_steering[bus];
  hyundai_canfd_steer_restore(primary);
  hyundai_canfd_aux_steering[bus] = auxiliary;
  return violation;
}
