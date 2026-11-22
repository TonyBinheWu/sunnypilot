import unittest

import numpy as np

from tools.training_studio.prepare import front_route


class FrontRouteTest(unittest.TestCase):
  def note(self, direction="left", kind="turn"):
    return {"maneuverType":kind, "maneuverModifier":direction,
            "allManeuvers":[{"type":kind, "modifier":direction, "distance":50.0}]}

  def test_aligned_student_and_teacher_intent(self):
    for direction, index in (("left",15),("right",10),("straight",8)):
      vector, intent, prompt = front_route(self.note(direction), .5, 10.)
      self.assertEqual(vector.shape,(47,))
      self.assertEqual(vector.dtype, np.float32)
      self.assertEqual(np.flatnonzero(vector[:-1]).tolist(),[index])
      self.assertAlmostEqual(float(vector[-1]),.45)
      self.assertEqual(intent,direction)
      self.assertIn(f"go {direction}",prompt)
      self.assertIn("45 meters",prompt)

  def test_missing_route_and_unsafe_or_inconsistent_commands(self):
    vector, intent, _ = front_route({},0,0)
    self.assertFalse(vector.any())
    self.assertEqual(intent,"follow")
    for note,age,speed in ((self.note(kind="merge"),0,1),(self.note(),2,1),
                           (self.note(),1,51),(dict(self.note(),maneuverModifier="right"),0,1),
                           (dict(self.note(),allManeuvers=[]),0,1)):
      with self.assertRaises(ValueError):
        front_route(note,age,speed)
