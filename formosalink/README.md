# FormosaPilot / FormosaLink 0.1

[繁體中文部署說明](docs/DEPLOY.zh-TW.md) · [English deployment guide](docs/DEPLOY.en.md) · [日本語の導入手順](docs/DEPLOY.ja.md)

FormosaPilot 是目前 sunnypilot 維護版本的品牌；FormosaLink 是可自架的獨立裝置管理平台。這次僅交付獨立配對、唯讀狀態 agent、三語手機儀表板與部署骨架。行車功能維持原分支行為。

FormosaPilot brands the maintained sunnypilot distribution. FormosaLink is its self-hosted companion. Release 0.1 implements independent pairing, read-only telemetry, a trilingual mobile dashboard and deployment scaffolding. Existing driving behavior is preserved.

FormosaPilot は保守対象の sunnypilot を基盤とするブランドです。FormosaLink はセルフホスト型の連携サービスです。0.1 では独立したペアリング、読み取り専用の状態送信、3 言語対応のモバイル画面、導入用構成を提供します。既存の運転支援動作は維持します。

## Scope / 範圍 / 範囲

- HTTPS origin: `https://formosapilot.dinglu-t.com`
- IIS physical destination: `\\192.168.20.145\htdocs\FormosaPilot`
- UI: 繁體中文 (default), English, 日本語. Buildless ES modules; no Node build or CDN required on IIS.
- Single owner, single Python worker, local SQLite. Multiple devices. No OIDC or PostgreSQL required for this batch.
- Dedicated Ed25519 device keys, expiring one-use pairing codes, fingerprint confirmation, signed/replay-protected connection authentication.
- WebSocket is preferred; proxies with incompatible upgrade handling use per-request signed HTTPS telemetry, retaining TLS verification, replay protection and revocation checks.
- Device state, temperatures, memory, storage, speed when valid, installed version/branch/commit. No location, driver-camera data, raw CAN, image streaming, remote commands or parameter reads.
- Agent default: **disabled**. Local CLI configuration is required; first batch does not add a device-screen pairing panel.
- Cloud outages do not gate the existing driving processes. Existing comma/sunnylink services are not redirected or silently disabled.
- SQLite stores the latest snapshot only (not journey history); audit is bounded to 10,000 events. Online requires a live authenticated WebSocket or recent signed HTTPS telemetry within 20 seconds. Invalid or old samples are shown as stale.
- First-batch backend auth uses one local owner password, PBKDF2-SHA256, HttpOnly/Secure/SameSite cookies and Origin checks. OIDC/multi-user sharing is deferred.
- For other users: deploy independent private instances today; central GitHub login requires the owner-isolation work in [MULTI_USER.md](docs/MULTI_USER.md). Public signup remains disabled.

## Source map

| Path | Responsibility |
| --- | --- |
| `openpilot/sunnypilot/formosalink/` | Shared v1 protocol, independent identity, local CLI and read-only agent |
| `formosalink/server/` | Owner authentication, persistent device registry, pairing, WSS ingestion, latest-state API |
| `formosalink/web/` | Taiwan-inspired mobile dashboard and generated FormosaPilot mark |
| `formosalink/deploy/` | IIS reverse proxy, Python launcher, optional Linux Compose skeleton |
| `tools/deploy/publish_formosalink_iis.ps1` | Manifest-owned deployment and file-hash verification |
| `tools/maintenance/sync_formosalink.py` | Copy only shared companion files and apply narrow hooks to another checkout |
| `formosalink/tests/` | Host tests with no native openpilot build or submodules required |

## Validation

```powershell
python -m pip install -r formosalink/requirements-test.txt requests websocket-client
python -m pytest formosalink/tests -q
node --test formosalink/tests/web.test.mjs
```

On restricted Windows hosts, use a new workspace-local `--basetemp build/formosalink-tests-<unique>` if the default temp directory is inaccessible. TestClient needs local socketpair access. CI runs Python 3.12 on Windows and Linux for both maintained branches; Node is needed only for the UI test, not production.

Both `hkg-enhanced` and `ccnc-port` use the same companion files and protocol. Only the optional manager entry and disabled-by-default Params key are added to each branch. Vehicle controllers, safety, models and AGNOS are not part of this change. See [protocol and upstream maintenance](docs/PROTOCOL.md).

Native pre-push checks and real-model simulator failures are recorded in [SIMULATION_2026_11_09.md](docs/SIMULATION_2026_11_09.md). All four PC UI/telemetry profiles passed; three model scenarios failed, including a failure reproduced on the pre-feature baseline. These are not physical-device driving acceptance results.

Not yet verified by host tests: end-to-end IIS ARR/WebSocket forwarding to the Python service, C3X/C4 runtime/build, physical vehicle telemetry, power/thermal behavior. Do not equate host tests with device validation. See the [validation record](docs/VALIDATION.md). The current logo and prompt are recorded in [BRAND.md](docs/BRAND.md).
