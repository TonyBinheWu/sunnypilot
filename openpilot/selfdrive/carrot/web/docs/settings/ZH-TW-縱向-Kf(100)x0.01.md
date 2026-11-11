<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_LONGTUNE" param="LongTuningKf" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 縱向 Kf(100)x0.01

**選單:** 駕駛控制 \> 巡航與車距 \> 加減速調校

---

<!-- CARROT:SETTING:BEGIN LongTuningKf -->
<a id="LongTuningKf"></a>

## 縱向 Kf(100)x0.01

`LongTuningKf`

在加速和制動方向預先應用目標加速度。現代、起亞和捷尼賽思的一般縱向控制固定為 Kf 1.0，因此不會顯示或應用此設定。 豐田/雷克薩斯的通用 Kf=1 固定，以避免與專用控制器重複補償；此設定隱藏且不應用儲存值。 已識別為 Ray EV Comma Pedal 控制時顯示此設定，並在約一秒內將儲存值應用於速度 PID。

<!-- CARROT:AUTO:BEGIN LongTuningKf -->
<!-- CARROT:AUTO:SOURCE facts="444d8e512a436dde7eb70be6e99ec92ab2653d27867994ed82cc44b7134714d7" semantic="b3ec7b2deffaf3c3c23388c2c4847d52984e1061625b5bb1cf8f304f7afcd1e5" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100`
- **範圍:** `0` ~ `200`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 加減速調校
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongTuningKf -->

<!-- CARROT:MANUAL:BEGIN LongTuningKf -->
<!-- CARROT:REVIEW reviewed-for="b3ec7b2deffaf3c3c23388c2c4847d52984e1061625b5bb1cf8f304f7afcd1e5" reviewed-at="2026-11-11T05:33:10.303272+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 動作

Ray EV 檢測到 Comma Pedal 且啟用 openpilot 縱向控制後，會顯示 Long Kp/Ki/Kf，並將儲存值用於速度 PID。啟動時讀取儲存值，執行期間約每秒更新一次。

其他現代/起亞/捷尼賽思配置的通用 Kp/Ki/Kf 固定為 1/0/1。豐田/雷克薩斯由專用車輛控制器補償加速度，通用增益固定為 0/0/1。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END LongTuningKf -->

<!-- CARROT:SETTING:END LongTuningKf -->
