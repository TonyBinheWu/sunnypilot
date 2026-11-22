"""On-road inputs shared by the internal, USB GPU and Jetlink driving models."""
import numpy as np

from openpilot.cereal import custom
from openpilot.selfdrive.modeld.constants import ModelConstants


_NO_COMMAND = custom.CarrotMan.new_message().as_reader()


def driver_maneuver_command(carrot_man):
  # The shared message also carries route-derived turns, forks and distances.
  # Only an explicit app lane-change command belongs in the maneuver FSM.
  if carrot_man.carrotCmd == "LANECHANGE" and carrot_man.carrotArg in ("LEFT", "RIGHT"):
    return custom.CarrotMan.new_message(carrotCmdIndex=carrot_man.carrotCmdIndex,
                                       carrotCmd="LANECHANGE", carrotArg=carrot_man.carrotArg).as_reader()
  return _NO_COMMAND


def driving_model_inputs(desire, is_rhd, lateral_time, longitudinal_time):
  # Each runtime clears absent navigation tensors on every inference, including
  # the first after a backend switch. Route guidance is consumed by the HUD.
  pulse = np.zeros(ModelConstants.DESIRE_LEN, dtype=np.float32)
  if 0 <= desire < len(pulse):
    pulse[desire] = 1
  return {'desire_pulse': pulse,
          'traffic_convention': np.array([not is_rhd, is_rhd], dtype=np.float32),
          'action_t': np.array([lateral_time, longitudinal_time], dtype=np.float32)}
