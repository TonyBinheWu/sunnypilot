# FormosaLink protocol v1 / 協定與共同維護

## Boundaries

The first batch has no command bus. Only signed enrollment, signed connection authentication, validated telemetry frames and acknowledgements exist. If a proxy cannot forward a valid WebSocket handshake, the agent uses signed HTTPS telemetry instead. Telemetry cannot invoke Params, shell commands, CAN publishers or the updater. Driver-camera, road-camera and location are excluded. No arbitrary cereal-service selection or Params enumeration is exposed.

## Authentication

Each local identity contains a UUID, dedicated Ed25519 private key and fixed origin. `POST /api/v1/agent/enroll` carries a signed envelope whose payload contains only the raw base64 public key. A matching UUID/public key can renew an unpaired code; an existing paired device returns its state, while revoked identities cannot re-enroll.

Envelopes have exactly `version`, `device_id`, `purpose`, `payload`, `timestamp`, `nonce`, `signature`. Signing input is UTF-8 JSON with sorted keys, compact separators, ASCII escaping and no nonfinite numbers, excluding `signature`. Purposes are `enroll` and `connect`. Timestamps tolerate 90 seconds of clock skew. UUID nonces are stored with a 180-second retention period to reject replay, including across server restarts. TLS remains mandatory outside loopback.

The server issues 12 random hexadecimal code characters (48 bits), stores only the code hash, expires it after 600 seconds and consumes it transactionally once an authenticated owner submits both code and 24-character SHA-256 public-key fingerprint. Global/IP request throttles and a 100-pending-device cap limit abuse. Pairing requires a local CLI request; no unattended claim button exists.

## WebSocket

The agent opens `wss://<origin>/api/v1/agent/ws` without browser Origin/cookies. First frame: a signed `connect` envelope with empty payload. Only paired, non-revoked identities are accepted. The server sends `{"type":"ready","version":1,"sample_interval":5}`. A new authenticated connection replaces the previous connection for that identity.

Every 5 seconds the agent sends `{"version":1,"sequence":0,"sampled_at":<unix_seconds>,"metrics":{...}}`. Sequence strictly increases within the connection. Maximum frame size is 16 KiB; telemetry cannot exceed one frame per second. Frames more than 90 seconds away from server time are rejected. The server accepts only fields declared by `METRIC_KEYS` and responds only `{"type":"ack","sequence":0}`. Missing/invalid ACKs are errors. No incoming command is executed. Idle sessions close after 20 seconds; authentication times out after 10 seconds. Reconnect uses exponential backoff with jitter, capped near 60 seconds. Device time must be synchronized.

## Freshness and persistence

HTTPS fallback: `POST /api/v1/agent/telemetry` carries the same snapshot as the payload of a signed envelope with purpose `telemetry`. Every request has a fresh nonce and is subject to the same timestamp, field allowlist, TLS and revocation checks. Only paired identities are accepted. The server persists nonce consumption before storing a snapshot. A recent signed HTTPS update counts as online for 20 seconds; no permanent session is inferred. The agent retries WebSocket after at most 60 HTTPS samples. Browser CSRF exemptions apply only to signature-authenticated device enrollment/telemetry routes, never owner operations.

Telemetry adapter checks source validity and producer monotonic timestamps (deviceState ≤5 seconds, carState ≤2 seconds); it does not apply high-frequency subscriber checks to a low-rate observer. Invalid deviceState yields null live fields and `sample_valid=false`; invalid carState yields null speed. Online requires an active socket and receipt within 20 seconds. Stale also includes invalid sample validity and sample timestamps more than 20 seconds from server time. The UI blanks current metrics on stale/offline data, retains clearly labelled timestamps/version information, and marks all retained data stale when API requests fail.

SQLite is local-disk only, schema v1, one owner and one backend process. It persists registered identities, revocations, hashed owner sessions, replay nonces, latest snapshots and bounded audit events. No trip history or metric archive is kept. Restart leaves devices offline until they reconnect. Revocation erases the snapshot and immediately closes an active socket. Config and identity migration beyond v1 are not implemented yet; future changes must add explicit migrations before incompatible schema updates.

## Upstream maintenance

`hkg-enhanced` and `ccnc-port` share the same files under `formosalink/` and `openpilot/sunnypilot/formosalink/`. Narrow hooks: `FormosaLinkEnabled` (persistent, default false, not backed up) and one optional PythonProcess. Keep existing branch/device/model/safety differences. The new UI uses FormosaPilot branding, but existing sunnypilot version headers and training/terms screens are not globally renamed in this batch.

Before syncing, keep a record of each branch HEAD and all submodule gitlinks. Run `tools/maintenance/sync_formosalink.py --target <checkout> --check` to compare owned files and the two hooks; without `--check`, it copies companion files and inserts missing hooks. It never replaces whole Params/process files. For updates to existing hook behavior, review and apply a small explicit patch to each branch. Treat changed cereal field names, Params lifecycle or manager process contracts as adapter changes. Maintain protocol compatibility between currently deployed agent and server; publish cloud and device changes separately.

Required checks: Python and UI contracts on both branches, C3X/C4 builds and real device telemetry validity, disconnect/revoke behavior, resource use and cloud-offline driving independence. Host tests alone do not establish vehicle behavior. No upstream merge, device release, firmware flash or production service startup is performed by the sync tool.
