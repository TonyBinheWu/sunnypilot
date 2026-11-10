import argparse
import json
import sys

import requests

from openpilot.sunnypilot.formosalink.identity import create, default_directory, read
from openpilot.sunnypilot.formosalink.i18n import MESSAGES
from openpilot.sunnypilot.formosalink.protocol import fingerprint, sign, validate_origin
from openpilot.sunnypilot.formosalink.pairing import pairing_url


def main():
  for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
      stream.reconfigure(encoding="utf-8")
  pre = argparse.ArgumentParser(add_help=False)
  pre.add_argument("--lang", choices=MESSAGES, default="zh-TW")
  language = pre.parse_known_args()[0].lang
  t = MESSAGES[language].__getitem__
  parser = argparse.ArgumentParser(description=t("description"))
  parser.add_argument("--lang", choices=MESSAGES, default="zh-TW", help=t("language"))
  parser.add_argument("--state-dir", default=str(default_directory()), help=t("state_dir"))
  commands = parser.add_subparsers(dest="command", required=True)
  setup = commands.add_parser("pair", help=t("pair_help"))
  setup.add_argument("--url", required=True, help=t("url_help"))
  setup.add_argument("--enable", action="store_true", help=t("enable_help"))
  commands.add_parser("status")
  commands.add_parser("disable")
  run = commands.add_parser("run")
  run.add_argument("--demo", action="store_true", help=t("demo_help"))
  args = parser.parse_args()
  if args.command == "disable":
    from openpilot.common.params import Params
    params = Params()
    params.put_bool("FormosaLinkRemoteSettings", False, block=True)
    params.put_bool("FormosaLinkEnabled", False, block=True)
    print(t("disabled"))
    return
  if args.command == "run":
    from openpilot.sunnypilot.formosalink.agent import run
    run(args.state_dir, demo=args.demo)
    return
  if args.command == "pair":
    origin = validate_origin(args.url)
    try:
      identity, private, public = read(args.state_dir)
    except FileNotFoundError:
      identity, private, public = create(args.state_dir, origin)
    if identity["origin"] != origin:
      raise SystemExit(t("other_server"))
    response = requests.post(origin + "/api/v1/agent/enroll", json=sign(private, identity["device_id"], "enroll", {"public_key": public}), timeout=15)
    response.raise_for_status()
    result = response.json()
    if result.get("fingerprint") != fingerprint(public):
      raise SystemExit(t("bad_fingerprint"))
    print("FormosaPilot → FormosaLink")
    print(t("device") + ":", identity["device_id"])
    if result.get("pair_code"):
      print(t("pair_url") + ":", pairing_url(origin, result))
      print(t("instructions"))
    else:
      print(t("paired"))
    if args.enable:
      from openpilot.common.params import Params
      Params().put_bool("FormosaLinkEnabled", True)
      print(t("enabled"))
  else:
    identity, _, public = read(args.state_dir)
    print(json.dumps({"device_id": identity["device_id"], "origin": identity["origin"], "fingerprint": fingerprint(public)}, indent=2))


if __name__ == "__main__":
  try:
    main()
  except (OSError, ValueError, requests.RequestException) as exc:
    language = next((sys.argv[i+1] for i,a in enumerate(sys.argv[:-1]) if a=="--lang"), "zh-TW")
    print(MESSAGES.get(language,MESSAGES["zh-TW"])["failed"] + " (" + type(exc).__name__ + ")", file=sys.stderr)
    raise SystemExit(1)
