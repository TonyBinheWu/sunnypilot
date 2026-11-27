"""Strict destination codec for the existing native NavDestination parameter."""
import json
import math


def destination(value):
  if not isinstance(value,str) or len(value)>512:
    raise ValueError("invalid_type")
  try:
    data=json.loads(value)
  except (ValueError,TypeError):
    raise ValueError("invalid_type") from None
  if not isinstance(data,dict) or set(data)!={"latitude","longitude","place_name"}:
    raise ValueError("invalid_type")
  for key,limit in (("latitude",90),("longitude",180)):
    v=data[key]
    if type(v) not in (int,float) or not math.isfinite(v) or not -limit<=v<=limit:
      raise ValueError("out_of_range")
  name=data["place_name"]
  if not isinstance(name,str) or not 1<=len(name)<=120 or any(ord(c)<32 for c in name):
    raise ValueError("invalid_type")
  return data


def encode(value):
  if value is None:
    return ""
  return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)


def entry(enabled):
  return {"key":"NavDestination","type":"STRING","widget":"navigation","enabled":enabled,"unit":"",
          "title":{"zh-TW":"導航目的地","en":"Navigation destination","ja":"ナビの目的地"},
          "group":{"zh-TW":"導航","en":"Navigation","ja":"ナビゲーション"},
          "description":{"zh-TW":"","en":"","ja":""}}
