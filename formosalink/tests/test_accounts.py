import json
import sqlite3
import io
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

from formosalink.server import oauth
from formosalink.server.app import create_app
from formosalink.server.config import initialize
from formosalink.server.store import Store, digest
from formosalink.tests.test_platform import ORIGIN, PASSWORD, enroll, login, pair


@pytest.fixture
def client(tmp_path, monkeypatch):
  initialize(tmp_path, ORIGIN, PASSWORD)
  (tmp_path / "github.json").write_text(json.dumps({"client_id": "test-client-id", "client_secret": "s"*40}))
  async def exchange(config, callback, code, verifier):
    assert callback == ORIGIN + "/api/v1/auth/github/callback"
    assert len(verifier) >= 43
    if code == "failure":
      raise httpx.ConnectError("unavailable")
    return code, "user-" + code
  monkeypatch.setattr(oauth, "exchange", exchange)
  with TestClient(create_app(tmp_path), base_url=ORIGIN) as value:
    yield value


def github_login(client, identity="101", link=False):
  if link:
    result = client.post("/api/v1/auth/github/link", json={}, headers={"Origin": ORIGIN})
    assert result.status_code == 200
    url = result.json()["url"]
  else:
    result = client.get("/api/v1/auth/github/start", follow_redirects=False)
    assert result.status_code == 303
    url = result.headers["location"]
  query = parse_qs(urlparse(url).query)
  assert parse_qs(urlparse(url).query, keep_blank_values=True)["scope"] == [""]
  assert query["code_challenge_method"] == ["S256"]
  assert len(query["code_challenge"][0]) == 43
  state = query["state"][0]
  result = client.get("/api/v1/auth/github/callback", params={"state": state, "code": identity}, follow_redirects=False)
  return state, result


def test_accounts_pairing_isolation_and_signed_telemetry(client):
  admin_device, _, _ = pair(client)
  _, result = github_login(client)
  assert result.headers["location"] == "/"
  first = client.get("/api/v1/auth/me").json()["user"]
  assert first["id"] != "local-admin"
  assert client.get("/api/v1/devices").json()["devices"] == []
  own, _, pending, _ = enroll(client)
  body = {"code": pending["pair_code"], "fingerprint": pending["fingerprint"], "name": "Own"}
  assert client.post("/api/v1/pair", json={**body, "owner_id": "local-admin"}, headers={"Origin": ORIGIN}).status_code == 422
  assert client.post("/api/v1/pair", json=body, headers={"Origin": ORIGIN}).status_code == 200
  assert [d["id"] for d in client.get("/api/v1/devices").json()["devices"]] == [own]
  assert client.post(f"/api/v1/devices/{admin_device}/revoke", json={}, headers={"Origin": ORIGIN}).status_code == 404
  assert client.app.state.store.get(admin_device)["state"] == "paired"
  assert client.post("/api/v1/auth/github/link", json={}, headers={"Origin": ORIGIN}).status_code == 403
  github_login(client, "202")
  assert client.get("/api/v1/devices").json()["devices"] == []
  assert client.post(f"/api/v1/devices/{own}/revoke", json={}, headers={"Origin": ORIGIN}).status_code == 404
  login(client)
  assert [d["id"] for d in client.get("/api/v1/devices").json()["devices"]] == [admin_device]
  github_login(client, "101")
  assert client.get("/api/v1/auth/me").json()["user"]["id"] == first["id"]
  assert client.post(f"/api/v1/devices/{own}/revoke", json={}, headers={"Origin": ORIGIN}).status_code == 200


def test_explicit_admin_link_preserves_devices_and_replay_fails(client):
  device_id, _, _ = pair(client)
  state, response = github_login(client, link=True)
  assert response.headers["location"] == "/"
  assert client.get("/api/v1/auth/me").json()["user"]["id"] == "local-admin"
  assert client.app.state.store.get(device_id)["owner_id"] == "local-admin"
  assert client.get("/api/v1/auth/github/callback", params={"state": state, "code": "202"}, follow_redirects=False).headers["location"] == "/?auth=failed"
  client.post("/api/v1/logout", json={}, headers={"Origin": ORIGIN})
  github_login(client)
  assert client.get("/api/v1/auth/me").json()["user"]["id"] == "local-admin"
  assert len(client.get("/api/v1/devices").json()["devices"]) == 1


def test_identity_cannot_be_taken_over_by_admin_link(client):
  github_login(client)
  original = client.get("/api/v1/auth/me").json()["user"]["id"]
  login(client)
  _, response = github_login(client, link=True)
  assert response.headers["location"] == "/?auth=failed"
  github_login(client)
  assert client.get("/api/v1/auth/me").json()["user"]["id"] == original


def test_state_browser_expiry_cancel_failure_and_csrf(client):
  assert client.post("/api/v1/auth/github/link", json={}).status_code == 403
  result = client.get("/api/v1/auth/github/start", follow_redirects=False)
  state = parse_qs(urlparse(result.headers["location"]).query)["state"][0]
  client.cookies.clear()
  assert client.get("/api/v1/auth/github/callback", params={"state": state, "code": "101"}, follow_redirects=False).headers["location"] == "/?auth=failed"
  _, result = github_login(client, "failure")
  assert result.headers["location"] == "/?auth=failed"
  result = client.get("/api/v1/auth/github/start", follow_redirects=False)
  state = parse_qs(urlparse(result.headers["location"]).query)["state"][0]
  with client.app.state.store.connection() as db:
    db.execute("UPDATE oauth_states SET expires=0")
  assert client.get("/api/v1/auth/github/callback", params={"state": state, "code": "101"}, follow_redirects=False).headers["location"] == "/?auth=failed"
  assert client.get("/api/v1/auth/me").json()["user"] is None


def test_logout_cancels_pending_admin_link(client):
  login(client)
  result = client.post("/api/v1/auth/github/link", json={}, headers={"Origin": ORIGIN})
  state = parse_qs(urlparse(result.json()["url"]).query)["state"][0]
  client.post("/api/v1/logout", json={}, headers={"Origin": ORIGIN})
  result = client.get("/api/v1/auth/github/callback", params={"state": state, "code": "101"}, follow_redirects=False)
  assert result.headers["location"] == "/?auth=failed"
  assert client.get("/api/v1/auth/me").json()["user"] is None


def test_disabled_oauth_keeps_password_login(tmp_path):
  initialize(tmp_path, ORIGIN, PASSWORD)
  with TestClient(create_app(tmp_path), base_url=ORIGIN) as client:
    assert client.get("/api/v1/auth/me").json() == {"user": None, "github_enabled": False}
    assert client.get("/api/v1/auth/github/start").status_code == 503
    login(client)
    assert client.get("/api/v1/auth/me").json()["user"]["id"] == "local-admin"


def test_v1_migration_preserves_sessions_keys_and_ownership(tmp_path):
  path = tmp_path / "legacy.sqlite3"
  with sqlite3.connect(path) as db:
    db.executescript("""
      CREATE TABLE devices(id TEXT PRIMARY KEY, public_key TEXT NOT NULL, fingerprint TEXT NOT NULL,
        name TEXT NOT NULL,state TEXT NOT NULL,pair_hash TEXT UNIQUE,pair_expires REAL,created_at REAL NOT NULL,last_seen REAL,snapshot TEXT);
      CREATE TABLE sessions(token_hash TEXT PRIMARY KEY,expires REAL NOT NULL);
      INSERT INTO devices VALUES('existing','key','fingerprint','existing','paired',NULL,NULL,1,NULL,NULL);
      INSERT INTO devices VALUES('revoked','key','fingerprint','revoked','revoked',NULL,NULL,1,NULL,NULL);
      PRAGMA user_version=1;
    """)
    db.execute("INSERT INTO sessions VALUES(?,99999999999)", (digest("legacy-session"),))
  store = Store(path)
  assert store.principal("legacy-session")["id"] == "local-admin"
  assert store.get("existing")["public_key"] == "key"
  assert len(store.devices()) == 2
  user = store.github_user("101", "renamable")
  assert store.devices(user) == []
  assert store.github_user("101", "renamed") == user
  assert store.github_user("202", "renamable") != user
  assert path.with_name(path.name + ".before-v2.sqlite3").exists()
  assert Store(path).principal("legacy-session")


@pytest.mark.anyio
async def test_real_exchange_contract(monkeypatch):
  original = httpx.AsyncClient
  def handler(request):
    if request.url.host == "github.com":
      assert b"code_verifier=verifier" in request.content
      return httpx.Response(200, json={"access_token": "gho_example"})
    assert request.url == "https://api.github.com/user"
    assert request.headers["Authorization"] == "Bearer gho_example"
    return httpx.Response(200, json={"id": 123, "login": "tester"})
  monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs))
  assert await oauth.exchange({"client_id": "id", "client_secret": "secret"}, ORIGIN, "code", "verifier") == ("123", "tester")


def test_configuration_retries_without_disclosing_secret(tmp_path, monkeypatch, capsys):
  monkeypatch.setattr("sys.argv", ["oauth", "--data-dir", str(tmp_path)])
  monkeypatch.setattr("builtins.input", lambda prompt: "test-client-id")
  values = iter(["", "opaque-secret.with+symbols=" + "x"*20])
  monkeypatch.setattr(oauth.getpass, "getpass", lambda prompt: next(values))
  oauth.main()
  config = oauth.settings(tmp_path)
  assert config["client_secret"].startswith("opaque-secret.")
  assert config["client_secret"] not in capsys.readouterr().out
  before = (tmp_path / "github.json").read_bytes()
  monkeypatch.setattr(oauth.getpass, "getpass", lambda prompt: "")
  with pytest.raises(SystemExit):
    oauth.main()
  assert (tmp_path / "github.json").read_bytes() == before


def test_private_stdin_configuration_rejects_incomplete_input(tmp_path, monkeypatch, capsys):
  monkeypatch.setattr("sys.argv", ["oauth", "--data-dir", str(tmp_path), "--stdin"])
  secret = "test-only-opaque+secret=" + "x"*20
  monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"client_id": "test-client-id", "client_secret": secret})))
  oauth.main()
  assert oauth.settings(tmp_path)["client_secret"] == secret
  assert secret not in capsys.readouterr().out
  for encoding in ("utf-8-sig", "utf-16"):
    payload = json.dumps({"client_id": "test-client-id", "client_secret": secret}).encode(encoding)
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(payload)))
    oauth.main()
    assert oauth.settings(tmp_path)["client_secret"] == secret
  for invalid in ("", "\x16", "test-client-id", "x"*20+"\n"):
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"client_id": "test-client-id", "client_secret": invalid})))
    with pytest.raises(SystemExit):
      oauth.main()
    assert oauth.settings(tmp_path)["client_secret"] == secret
