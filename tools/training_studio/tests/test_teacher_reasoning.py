import unittest
from tools.training_studio.teacher_reasoning_train import decision_text


class DecisionLabelsTest(unittest.TestCase):
  def test_clear_turns_retain_driver_direction_instead_of_straight_template(self):
    for direction in ('left','right'):
      for scenario in (direction+'_turn','yield_'+direction,direction+'_arrow'):
        text=decision_text({'scenario':scenario,'stop_required':False})
        self.assertTrue(text.startswith('Proceed'));self.assertIn(direction+' turn',text);self.assertNotIn('straight',text)

  def test_blocked_pedestrians_wait_for_entire_roadway_and_clear_scenes_may_proceed(self):
    text=decision_text({'scenario':'pedestrian','stop_required':True})
    self.assertTrue(text.startswith('Wait'));self.assertIn('completely left the roadway',text)
    for scenario in ('red_light','yield_left','yield_right','left_arrow','right_arrow'):
      self.assertTrue(decision_text({'scenario':scenario,'stop_required':True}).startswith('Wait'))
    for scenario in ('pedestrian','red_light','lane_center'):
      self.assertTrue(decision_text({'scenario':scenario,'stop_required':False}).startswith('Proceed'))
    with self.assertRaises(ValueError):decision_text({'scenario':'lane_center','stop_required':True})


if __name__=='__main__':unittest.main()
