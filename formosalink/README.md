# FormosaPilot / FormosaLink 0.6.0

[繁體中文部署說明](docs/DEPLOY.zh-TW.md) · [English deployment guide](docs/DEPLOY.en.md) · [日本語の導入手順](docs/DEPLOY.ja.md)

[QR 配對 / QR pairing / QR 登録](docs/QR_PAIRING.md)：裝置設定顯示短效 QR，手機以 GitHub 登入並確認；網頁不再顯示管理者密碼及手動配對輸入。

FormosaPilot 是目前 sunnypilot 維護版本的品牌；FormosaLink 是可自架的獨立裝置管理平台。目前提供 GitHub 多用戶登入、帳號裝置隔離、車端 QR 配對、監看、停車設定同步與三語手機儀表板。行車功能維持原分支行為。

FormosaPilot brands the maintained sunnypilot distribution. FormosaLink is its self-hosted companion. It provides GitHub accounts, isolated device ownership, native QR pairing, telemetry, parked settings sync and a trilingual mobile dashboard. Existing driving behavior is preserved.

FormosaPilot は保守対象の sunnypilot を基盤とするブランドです。FormosaLink はセルフホスト型の連携サービスです。GitHub ログイン、所有者別のデバイス管理、本体の QR 登録、状態送信、停車中の遠隔設定、3 言語のモバイル画面を提供します。既存の運転支援動作は維持します。

## Scope / 範圍 / 範囲

- HTTPS origin: `https://formosapilot.dinglu-t.com`
- IIS physical destination: `\\192.168.20.145\htdocs\FormosaPilot`
- UI: 繁體中文 (default), English, 日本語. Buildless ES modules; no Node build or CDN required on IIS.
- GitHub accounts with owner-scoped devices, single Python worker, local SQLite. Existing administrator credentials and pairing data migrate in place.
- Dedicated Ed25519 device keys, expiring one-use pairing codes, fingerprint confirmation, signed/replay-protected connection authentication.
- WebSocket is preferred; proxies with incompatible upgrade handling use per-request signed HTTPS telemetry, retaining TLS verification, replay protection and revocation checks.
- Device state, temperatures, memory, storage, speed when valid, installed version/branch/commit. No live location, driver-camera data or raw CAN. Typed parked settings use an explicit allowlist. The separately launched media preview publisher can upload signed, bounded JPEG frames; native camera capture is not connected yet.
- Agent default: **disabled**. Explicit offroad opt-in is available in Settings → Device → FormosaLink on both C3X and C4. Scan its QR with a phone to pair without typing codes or fingerprints.
- Cloud outages do not gate the existing driving processes. Existing comma/sunnylink services are not redirected or silently disabled.
- SQLite stores the latest snapshot only (not journey history); audit is bounded to 10,000 events. Online requires a live authenticated WebSocket or recent signed HTTPS telemetry within 20 seconds. Invalid or old samples are shown as stale.
- GitHub OAuth uses one-time browser-bound state and S256 PKCE. The local administrator password remains a fallback. Device operations enforce ownership on the server.
- Setup, private OAuth configuration, explicit administrator linking and migration recovery: [MULTI_USER.md](docs/MULTI_USER.md). GitHub login remains disabled until the host has OAuth credentials.

## Source map

| Path | Responsibility |
| --- | --- |
| `openpilot/sunnypilot/formosalink/` | Shared v1 protocol, independent identity, local CLI, telemetry and guarded parked settings |
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

On restricted Windows hosts, use a new workspace-local `--basetemp build/formosalink-tests-<unique>` if the default temp directory is inaccessible. TestClient needs local socketpair access. CI runs Python 3.12/3.14 on Windows and Linux for both maintained branches; Node is needed only for the UI test, not production.

Both `hkg-enhanced` and `ccnc-port` use the same companion files and protocol. Narrow hooks add the optional manager process, disabled-by-default Params key and offroad QR entries; branch-specific settings are retained. Vehicle controllers, safety, models and AGNOS are not part of this change. See [protocol and upstream maintenance](docs/PROTOCOL.md).

Native pre-push checks and real-model simulator failures are recorded in [SIMULATION_2026_11_09.md](docs/SIMULATION_2026_11_09.md). All four PC UI/telemetry profiles passed; three model scenarios failed, including a failure reproduced on the pre-feature baseline. These are not physical-device driving acceptance results.

Not yet verified by host tests: end-to-end IIS ARR/WebSocket forwarding to the Python service, C3X/C4 runtime/build, physical vehicle telemetry, power/thermal behavior. Do not equate host tests with device validation. See the [validation record](docs/VALIDATION.md). The current logo and prompt are recorded in [BRAND.md](docs/BRAND.md).


[裝置資訊、停車設定與 IIS 升級 / Device settings / 停車中の設定](docs/OFFROAD_SETTINGS.md)


[健康總覽、SOC、eGPU、主題與導航 / Health and navigation / 状態とナビ](docs/HEALTH_NAVIGATION.md)

[Hyundai／Kia 自動辨識與 SOC 訊號審查 / SOC audit / SOC 検査](docs/HYUNDAI_SOC.md)

[設定控制項、逐項同步與衝突處理 / Settings controls and conflicts / 設定と競合](docs/SETTINGS_UI.md)

[影音整合階段、發送器與 IIS 更新 / Media integration / メディア統合](docs/MEDIA_INTEGRATION.md)
