"""GitHub identity only. Tokens are used once and never persisted."""
import base64
import getpass
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import urlencode

import httpx


def settings(directory):
  path = Path(directory) / "github.json"
  if not path.exists():
    return None
  value = json.loads(path.read_text(encoding="utf-8"))
  if not re.fullmatch(r"[A-Za-z0-9_.-]{10,128}", value["client_id"]) or not re.fullmatch(r"[A-Za-z0-9_\-]{20,256}", value["client_secret"]):
    raise ValueError("invalid GitHub OAuth configuration")
  return value


def authorize_url(config, callback, state, verifier):
  challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
  return "https://github.com/login/oauth/authorize?" + urlencode({
    "client_id": config["client_id"], "redirect_uri": callback, "state": state,
    "scope": "", "code_challenge": challenge, "code_challenge_method": "S256", "prompt": "select_account"})


async def exchange(config, callback, code, verifier):
  async with httpx.AsyncClient(timeout=15, follow_redirects=False, trust_env=False) as client:
    response = await client.post("https://github.com/login/oauth/access_token", headers={"Accept": "application/json"}, data={
      "client_id": config["client_id"], "client_secret": config["client_secret"], "code": code,
      "redirect_uri": callback, "code_verifier": verifier})
    response.raise_for_status()
    token = response.json().get("access_token")
    if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_]{1,512}", token):
      raise ValueError("GitHub authorization failed")
    response = await client.get("https://api.github.com/user", headers={"Authorization": "Bearer " + token,
      "Accept": "application/vnd.github+json", "User-Agent": "FormosaLink", "X-GitHub-Api-Version": "2022-11-28"})
    response.raise_for_status()
    user = response.json()
    if type(user.get("id")) is not int or user["id"] <= 0 or not isinstance(user.get("login"), str) or not re.fullmatch(r"[A-Za-z0-9-]{1,39}", user["login"]):
      raise ValueError("invalid GitHub identity")
    return str(user["id"]), user["login"]


def main():
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("--data-dir", required=True)
  parser.add_argument("--lang", choices=("zh-TW", "en", "ja"), default="zh-TW")
  args = parser.parse_args()
  prompts = {"zh-TW": ("GitHub Client ID：", "GitHub Client Secret（隱藏輸入）：", "OAuth 設定已儲存；請重新啟動後端。"),
             "en": ("GitHub Client ID: ", "GitHub Client Secret (hidden): ", "OAuth configuration saved; restart the backend."),
             "ja": ("GitHub Client ID：", "GitHub Client Secret（非表示）：", "OAuth 設定を保存しました。バックエンドを再起動してください。")}[args.lang]
  value = {"client_id": input(prompts[0]).strip(), "client_secret": getpass.getpass(prompts[1]).strip()}
  # Validate before replacing any existing private configuration.
  if not re.fullmatch(r"[A-Za-z0-9_.-]{10,128}", value["client_id"]) or not re.fullmatch(r"[A-Za-z0-9_\-]{20,256}", value["client_secret"]):
    raise SystemExit("Invalid Client ID / Client Secret")
  path = Path(args.data_dir) / "github.json"
  temporary = path.with_suffix(".tmp")
  with temporary.open("w", encoding="utf-8") as output:
    os.chmod(temporary, 0o600)
    json.dump(value, output)
  os.replace(temporary, path)
  print(prompts[2])


if __name__ == "__main__":
  main()
