# Speed and deceleration

[한국어](../ko/speed-deceleration.md)

With openpilot longitudinal control engaged, the planner combines the model acceleration and stop request, the lead-vehicle MPC and the cruise-speed ceiling. The driving personality selects the following time. Vision curve, map curve and speed-limit assistance are available under Daily Driving. The vehicle interface supplies actuator delay and stop calibration. The previous speed/deceleration and PID panels have been removed.

At standstill, a model or MPC stop request holds the stopping state. Once both release, a pressed brake, active soft hold or a standstill request from factory cruise still prevents departure. A vehicle using factory longitudinal control follows its own restart rules. The driver must watch each signal, crossing and lead vehicle.

[Related driving settings](cruise-gap.md)
