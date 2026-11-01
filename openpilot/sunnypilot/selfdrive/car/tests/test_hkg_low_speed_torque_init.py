"""Regression tests for HKG low-speed torque initialization in the live card startup path."""

from unittest.mock import Mock

from openpilot.sunnypilot.selfdrive.car.interfaces import initialize_params


def test_hkg_torque_enabled_is_forwarded_to_opendbc():
  params = Mock()
  params.get.side_effect = lambda key, return_default=False: key == "HkgLowSpeedTorque"

  forwarded = initialize_params(params)
  values = {name: value for entry in forwarded for name, value in entry.items()}

  assert values["HkgLowSpeedTorque"] is True
  assert values["HyundaiLongitudinalTuning"] is False
  params.get.assert_any_call("HkgLowSpeedTorque", return_default=True)


def test_hkg_torque_disabled_is_forwarded_to_opendbc():
  params = Mock()
  params.get.return_value = False

  forwarded = initialize_params(params)
  values = {name: value for entry in forwarded for name, value in entry.items()}

  assert "HkgLowSpeedTorque" in values
  assert values["HkgLowSpeedTorque"] is False
  params.get.assert_any_call("HkgLowSpeedTorque", return_default=True)
