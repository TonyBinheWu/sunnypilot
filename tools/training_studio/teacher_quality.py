"""Strict offline checkpoint comparisons; physical qualification remains mandatory."""
import math


def quality_conditions(candidate,baseline):
  candidate=candidate or {};baseline=baseline or {}
  names=('validation_loss','red_safe_count','red_hold_speed_mse','lateral_trajectory_mse','go_velocity_mse')
  def numeric(value):return type(value) in (int,float) and math.isfinite(value) and value>=0
  checks={name:numeric(candidate.get(name)) and numeric(baseline.get(name)) and
    (candidate[name]>=baseline[name] if name=='red_safe_count' else candidate[name]<=baseline[name]) for name in names}
  checks['same_samples']=all(type(baseline.get(key)) is int and type(candidate.get(key)) is int and baseline[key]>0 and candidate.get(key)==baseline[key] for key in ('red_samples','go_samples'))
  checks['valid_stop_counts']=all(type(row.get('red_safe_count')) is int and type(row.get('red_samples')) is int and 0<=row['red_safe_count']<=row['red_samples'] for row in (candidate,baseline))
  return checks


def checkpoint_quality(candidate,baseline,guard_reference=None):
  groups={'full':quality_conditions(candidate,baseline)}
  if baseline.get('validation_guard') is not None or guard_reference is not None:
    groups['validation_guard']=quality_conditions(candidate.get('validation_guard'),baseline.get('validation_guard'))
    if guard_reference is not None:groups['guard_reference']=quality_conditions(candidate.get('validation_guard'),guard_reference)
  if baseline.get('parent_validation') is not None or baseline.get('parent_validation_reference') is not None:
    groups['parent_validation']=quality_conditions(candidate.get('parent_validation'),baseline.get('parent_validation'))
    groups['parent_reference']=quality_conditions(candidate.get('parent_validation'),baseline.get('parent_validation_reference'))
    parent_guard=(baseline.get('parent_validation_reference') or {}).get('validation_guard')
    if parent_guard is not None:groups['parent_fixed_guard']=quality_conditions(candidate.get('validation_guard'),parent_guard)
  return {'passed':all(all(group.values()) for group in groups.values()),'conditions':groups}
