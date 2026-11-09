# 驗證紀錄 / Validation / 検証記録

Date: 2026-11-09 (Asia/Taipei). First batch, FormosaLink 0.1.0 / protocol v1.

This is the initial implementation record. Later service fixes have 29 passing backend tests on isolated Python 3.14.10 plus two passing UI tests. For the actual pre-push native UI/telemetry matrix, model failures and baseline comparison, see [SIMULATION_2026_11_09.md](SIMULATION_2026_11_09.md). Deployment state below reflects the initial publication, not the subsequent service startup.

| Check | hkg-enhanced | ccnc-port |
| --- | --- | --- |
| Python host suite, including real HTTP/WebSocket client | 25 passed | 25 passed |
| UI language completeness and rendering safety | 2 passed | 2 passed |
| Architecture module inventory | 15 definitions valid | 15 definitions valid |
| Shared companion source comparison | Identical | Identical |

Host: Windows, Python 3.13.9. CI is configured for Python 3.12 on Windows/Linux but has not been run remotely. Three dependency deprecation warnings originate from uvicorn's default websockets legacy transport; they do not indicate failing assertions.

Browser QA: 390 × 844 mobile viewport; Traditional Chinese, English and Japanese; owner login, live labelled demo telemetry, pairing form, language switching and desktop layout. Only explicit test data was used, never real vehicle data. The preview server and demo agent were stopped after screenshots were saved under the workspace's ignored `build/` directory.

Deployment: files copied to `\\192.168.20.145\htdocs\FormosaPilot`, with SHA-256 verification. HTTPS homepage returned 200; backend health endpoint returned 502; a direct request for protected App_Data Python source returned 404. Backend initialization, owner password, Windows process startup and end-to-end IIS WebSocket forwarding remain to be completed on the server. No production credentials are generated or copied by the deployment script.

尚未完成 C3X／C4 原生建置、實機採樣、車上負載與雲端斷線行車驗證。本次不修改車型、控制器、safety、模型或 AGNOS。兩分支的修改尚未提交或推送。

C3X/C4 native builds, physical-device telemetry, runtime resource use and cloud-offline driving verification remain outstanding. Vehicle controllers, safety, models and AGNOS are outside this change. Changes in both branches remain uncommitted and unpushed.

C3X／C4 のビルド、実機の状態取得、負荷、クラウド切断時の運転支援動作は未検証です。車両制御、safety、モデル、AGNOS は変更していません。両ブランチともコミット・プッシュは行っていません。
