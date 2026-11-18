import unittest
from tools.training_studio.teacher_reasoning_train import decision_text,maneuver_class,balanced_maneuver_weights,balanced_scene_weights,navigation_order


class DecisionLabelsTest(unittest.TestCase):
  def test_actual_sampling_balances_rare_scenes_and_retains_coverage_across_epochs(self):
    from collections import Counter
    rows=[{'scenario':scene,'stop_required':stop} for scene,stop in [('red_light',True)]*20+[('left_arrow',True)]*2+[('red_light',False)]*8+[('left_turn',False)]*2+[('right_turn',False)]*2]
    order=navigation_order(rows,0)
    self.assertEqual(order,navigation_order(rows,0))
    self.assertEqual(Counter(maneuver_class(rows[i]) for i in order),dict.fromkeys(('wait','straight','left','right'),9))
    waits=Counter(rows[i]['scenario'] for i in order if rows[i]['stop_required'])
    self.assertLessEqual(abs(waits['red_light']-waits['left_arrow']),1)
    self.assertGreater(waits['left_arrow'],2)
    self.assertEqual({i for epoch in range(12) for i in navigation_order(rows,epoch)},set(range(len(rows))))
    with self.assertRaises(ValueError):navigation_order(rows[:-2],0)

  def test_navigation_profile_distinguishes_all_four_first_decisions(self):
    for scenario,stop,expected in (('red_light',True,'Wait'),('red_light',False,'Proceed'),('left_turn',False,'Left'),('right_turn',False,'Right')):
      self.assertTrue(decision_text({'scenario':scenario,'stop_required':stop},True).startswith(expected+' '))
    for scenario in ('yield_left','left_arrow'):
      self.assertEqual(maneuver_class({'scenario':scenario,'stop_required':True}),'wait')
      self.assertEqual(maneuver_class({'scenario':scenario,'stop_required':False}),'left')

  def test_class_balancing_preserves_equal_total_supervision_with_unequal_counts(self):
    rows=[{'scenario':scene,'stop_required':stop} for scene,stop in [('red_light',True)]*8+[('red_light',False)]*4+[('left_turn',False)]*2+[('right_turn',False)]]
    weights=balanced_maneuver_weights(rows)
    for key in ('wait','straight','left','right'):
      self.assertAlmostEqual(sum(weights[key] for row in rows if maneuver_class(row)==key),len(rows)/4)
    with self.assertRaises(ValueError):balanced_maneuver_weights(rows[:-1])

  def test_rare_arrow_stop_retains_equal_visual_condition_mass_within_wait_class(self):
    rows=[{'scenario':scene,'stop_required':stop} for scene,stop in [('red_light',True)]*20+[('left_arrow',True)]*2+[('red_light',False)]*8+[('left_turn',False)]*2+[('right_turn',False)]*2]
    weights=balanced_scene_weights(rows)
    for key in ('wait','straight','left','right'):
      self.assertAlmostEqual(sum(weights[key+':'+row['scenario']] for row in rows if maneuver_class(row)==key),len(rows)/4)
    self.assertAlmostEqual(20*weights['wait:red_light'],2*weights['wait:left_arrow'])
    self.assertGreater(weights['wait:left_arrow'],weights['wait:red_light'])

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
