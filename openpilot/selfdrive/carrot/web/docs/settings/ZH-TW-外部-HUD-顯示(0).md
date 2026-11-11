<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="HUD_BASIC" param="ClusterHud" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 外部 HUD 顯示(0)

**選單:** 顯示 \> 外部HUD \> 基本

---

<!-- CARROT:SETTING:BEGIN ClusterHud -->
<a id="ClusterHud"></a>

## 外部 HUD 顯示(0)

`ClusterHud`

0: 關閉 1: TURZX 9.2 英寸 適用於直接連線本機的 USB HUD。連線到 Jetson USB 的 HUD 自動執行，不受此設定影響。熄火後關閉螢幕；HUD 除錯設定控制常亮。支援的 Jetson 執行時在推理期間透過 USB 接收 HUD、導航和訊號燈資訊；舊接收器更新前保留 Wi-Fi。Jetson 目標輸出為 10 FPS。

<!-- CARROT:AUTO:BEGIN ClusterHud -->
<!-- CARROT:AUTO:SOURCE facts="98a872c49110dd90640cfb884c233ac8c0e5d7651f5ec230aeae40ad829fb227" semantic="9edf824457ea89ad8d62580c7ca4d5e4fc5c4e9c21e0b81860547c9d4b2bb10e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 顯示 \> 外部HUD \> 基本
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHud -->

<!-- CARROT:MANUAL:BEGIN ClusterHud -->
<!-- CARROT:REVIEW reviewed-for="17e8e51b49d27978d564c982b7216d47db6b18c9d4a636e239f4306d3b9cdf96" reviewed-at="2026-10-16T21:40:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

啟用或關閉直接 USB 或已註冊的 S3 HUD。連線到 Jetson 的 HUD 不受此設定影響，會自動執行。

最新 C4 和 S3 韌體 1.2.0 自動使用 H.264；舊韌體或未收到功能確認時使用 JPEG。目標為 15 FPS，eGPU 啟用時最高 10 FPS；實際速度取決於畫面和無線連線。

透過[安裝、韌體與註冊指南](https://upload.shind0.synology.me/models/carrot-s3/index.html)將 S3 更新一次至 1.2.0。保留 Wi-Fi/C4 註冊，在同一 2.4GHz 網路自動重連。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ClusterHud -->

<!-- CARROT:SETTING:END ClusterHud -->
