import getpass
import hashlib
import json
import os
import secrets
from pathlib import Path

from openpilot.sunnypilot.formosalink.protocol import validate_origin
from openpilot.sunnypilot.formosalink.i18n import MESSAGES


def password_hash(password, salt):
  return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600000).hex()


def initialize(directory, origin, password):
  directory = Path(directory).resolve()
  origin = validate_origin(origin)
  if len(password) < 14 or len(password) > 256:
    raise ValueError("owner password must be 14–256 characters")
  directory.mkdir(parents=True, exist_ok=True, mode=0o700)
  salt = secrets.token_hex(16)
  config = {"origin": origin, "password_salt": salt, "password_hash": password_hash(password, salt)}
  path = directory / "config.json"
  with path.open("x", encoding="utf-8") as file:
    os.chmod(path, 0o600)
    json.dump(config, file)
  return path


def load(directory):
  directory = Path(directory).resolve()
  config = json.loads((directory / "config.json").read_text(encoding="utf-8"))
  config["origin"] = validate_origin(config["origin"])
  return directory, config


def main():
  import argparse
  parser = argparse.ArgumentParser(description="Initialize FormosaLink owner credentials outside the IIS web root")
  parser.add_argument("--data-dir", required=True)
  parser.add_argument("--origin", required=True)
  parser.add_argument("--lang", choices=MESSAGES, default="zh-TW")
  args = parser.parse_args()
  t = MESSAGES[args.lang].__getitem__
  password = getpass.getpass(t("password"))
  if password != getpass.getpass(t("confirm")):
    raise SystemExit(t("mismatch"))
  try:
    print(t("initialized"), initialize(args.data_dir, args.origin, password))
  except (OSError, ValueError) as exc:
    raise SystemExit(t("failed") + " (" + type(exc).__name__ + ")") from None


if __name__ == "__main__":
  main()
