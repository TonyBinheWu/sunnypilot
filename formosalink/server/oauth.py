"""GitHub identity only. Tokens are used once and never persisted."""
import base64
import getpass
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

import httpx


def valid_client_id(value):
  return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.-]{10,128}", value) is not None


def valid_client_secret(value):
  # OAuth client secrets are opaque; do not assume GitHub's current prefix or alphabet.
  return isinstance(value, str) and 20 <= len(value) <= 512 and all(33 <= ord(char) <= 126 for char in value)


def settings(directory):
  path = Path(directory) / "github.json"
  if not path.exists():
    return None
  value = json.loads(path.read_text(encoding="utf-8"))
  if not valid_client_id(value["client_id"]) or not valid_client_secret(value["client_secret"]):
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
  parser.add_argument("--stdin", action="store_true", help="Read private configuration from standard input, never command-line arguments")
  args = parser.parse_args()
  prompts = {"zh-TW": ("GitHub Client ID：", "GitHub Client Secret（隱藏輸入）：", "OAuth 設定已儲存；請重新啟動後端。"),
             "en": ("GitHub Client ID: ", "GitHub Client Secret (hidden): ", "OAuth configuration saved; restart the backend."),
             "ja": ("GitHub Client ID：", "GitHub Client Secret（非表示）：", "OAuth 設定を保存しました。バックエンドを再起動してください。")}[args.lang]
  errors = {
    "zh-TW": ("Client ID 格式不正確，請從 OAuth App 複製 Client ID。", "Secret 未完整輸入（需 20–512 個可列印英數符號）。請貼上完整 Client Secret，不是 App 名稱或 Client ID。", "輸入已取消；原設定不變。"),
    "en": ("Invalid Client ID. Copy it from the OAuth App.", "Secret is incomplete (20–512 printable ASCII characters). Paste the full Client Secret, not the app name or Client ID.", "Cancelled; existing configuration is unchanged."),
    "ja": ("Client ID が正しくありません。OAuth App からコピーしてください。", "Secret が不完全です（表示可能な ASCII 文字 20～512 文字）。アプリ名や Client ID ではなく、完全な Client Secret を貼り付けてください。", "キャンセルしました。既存設定は変更しません。")}[args.lang]
  value = None
  if args.stdin:
    try:
      value = json.loads(sys.stdin.read(4096))
    except (ValueError, UnicodeError):
      raise SystemExit(errors[2]) from None
    if not isinstance(value, dict) or not valid_client_id(value.get("client_id")):
      raise SystemExit(errors[0])
    if not valid_client_secret(value.get("client_secret")) or value["client_secret"] == value["client_id"]:
      raise SystemExit(errors[1])
    value = {"client_id": value["client_id"], "client_secret": value["client_secret"]}
  else:
    try:
      for _ in range(3):
        client_id = input(prompts[0]).strip()
        if not valid_client_id(client_id):
          print(errors[0])
          continue
        secret = getpass.getpass(prompts[1]).strip()
        if not valid_client_secret(secret) or secret == client_id:
          print(errors[1])
          continue
        value = {"client_id": client_id, "client_secret": secret}
        break
    except (KeyboardInterrupt, EOFError):
      pass
  # Validate before replacing any existing private configuration.
  if value is None:
    raise SystemExit(errors[2])
  path = Path(args.data_dir) / "github.json"
  temporary = path.with_suffix(".tmp")
  with temporary.open("w", encoding="utf-8") as output:
    os.chmod(temporary, 0o600)
    json.dump(value, output)
  os.replace(temporary, path)
  print(prompts[2])


if __name__ == "__main__":
  main()
