"""Build a teacher receipt from an actual completed Edge closed-loop qualification batch."""
import argparse
import hashlib
import json
from pathlib import Path

from tools.training_studio.store import read_json,write_json
from tools.training_studio.engine import TEACHER_REVISION
from openpilot.sunnypilot.formosalink.training_protocol import digest_file


def qualify(batch,output):
  batch=Path(batch)
  summary=read_json(batch/'qualification.json',{})
  results=list(batch.glob('*/result.json'))
  if summary.get('passed') is not True or not results:
    raise ValueError('teacher batch did not pass; no qualification receipt produced')
  cases=[]
  provenance=None
  scenarios=set()
  for path in results:
    result=read_json(path)
    recorded=read_json(path.parent/'provenance.json')['provenance']
    checksum=hashlib.sha256(json.dumps(recorded,sort_keys=True).encode()).hexdigest()
    if result.get('backend')!='nvidia_alpamayo2_edge' or result.get('revision')!=TEACHER_REVISION or result.get('status')!='pass' or result.get('failures'):
      raise ValueError('failed or foreign teacher episode')
    if result.get('model_provenance_sha256')!=checksum or (provenance is not None and provenance!=recorded):
      raise ValueError('mixed teacher versions in qualification')
    if result.get('model_inputs_include_signal_ground_truth') is not False or result.get('scripted_fallback') is not False:
      raise ValueError('teacher used diagnostic/reference input')
    provenance=recorded
    scenarios.add(result['scenario'])
    cases.append({'scenario':result['scenario'],'evidence_sha256':digest_file(path),'passed':True})
  required={'lane_center','red_light','pedestrian','left_turn','right_turn','yield_left','yield_right','left_arrow','right_arrow'}
  if not required<=scenarios:
    raise ValueError('teacher curriculum incomplete: '+','.join(sorted(required-scenarios)))
  receipt={'passed':True,'input_profile':'experimental_front_only','provenance':provenance,'cases':cases,
    'qualification_sha256':digest_file(batch/'qualification.json')}
  write_json(output,receipt)
  return receipt


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--batch',type=Path,required=True)
  parser.add_argument('--output',type=Path,required=True)
  args=parser.parse_args()
  print(json.dumps(qualify(args.batch,args.output)))


if __name__=='__main__':
  main()
