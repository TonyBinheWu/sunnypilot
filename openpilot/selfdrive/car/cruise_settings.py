"""Periodic cruise preferences, read outside card's CAN processing loop."""


CRUISE_PARAM_READERS = {
  'SoftHoldOnCancel': 'get_bool',
  'AutoGasSyncSpeed': 'get_int',
  'SpeedFromPCM': 'get_int',
  'CruiseSpeedUnit': 'get_int',
  'CruiseButtonLongDelay': 'get_int',
  'CruiseSpeedUnitBasic': 'get_int',
  'PaddleMode': 'get_int',
  'CruiseButtonMode': 'get_int',
  'CancelButtonMode': 'get_int',
  'LfaButtonMode': 'get_int',
  'DisengageOnAccelerator': 'get_bool',
  'AutoRoadSpeedLimitOffset': 'get_int',
  'AutoCruiseControl': 'get_int',
  'AutoGasTokSpeed': 'get_int',
  'AutoGasCancelSpeed': 'get_int',
  'ApplyModelSpeed': 'get_float',
  'AutoSpeedUptoRoadSpeedLimit': 'get_float',
  'AutoRoadSpeedAdjust': 'get_float',
  'UseLaneLineSpeed': 'get_int',
  'AutoNaviSpeedSafetyFactor': 'get_float',
  'CruiseOnDist': 'get_float',
  'CruiseSpeed1': 'get_float',
  'CruiseSpeed2': 'get_float',
  'CruiseSpeed3': 'get_float',
  'CruiseSpeed4': 'get_float',
  'CruiseSpeed5': 'get_float',
}



def read_cruise_settings(params):
  # Build completely before publishing: the CAN thread never sees a partial refresh.
  return {key: getattr(params, method)(key) for key, method in CRUISE_PARAM_READERS.items()}
