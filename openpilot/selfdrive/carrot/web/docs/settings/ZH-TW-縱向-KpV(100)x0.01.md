<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_LONGTUNE" param="LongTuningKpV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 縱向 KpV(100)x0.01

**選單:** 駕駛控制 \> 巡航與車距 \> 加減速調校

---

<!-- CARROT:SETTING:BEGIN LongTuningKpV -->
<a id="LongTuningKpV"></a>

## 縱向 KpV(100)x0.01

`LongTuningKpV`

縱向控制比例增益。現代、起亞和捷尼賽思的一般縱向控制固定為 Kp 1.0，因此不會顯示或應用此設定。 豐田/雷克薩斯的通用 Kp=0 固定，以避免與專用控制器重複補償；此設定隱藏且不應用儲存值。 已識別為 Ray EV Comma Pedal 控制時顯示此設定，並在約一秒內將儲存值應用於速度 PID。

<!-- CARROT:AUTO:BEGIN LongTuningKpV -->
<!-- CARROT:AUTO:SOURCE facts="a1782a67c2bb1cb545dd9f075e237dfff3de0fe13dc73724cb9e91ac186dbdaa" semantic="da83b19cd7c1eaed65e221d1571b66a8f33f00b0c83097c2f56007bccd5323c1" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100`
- **範圍:** `0` ~ `200`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 加減速調校
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongTuningKpV -->

<!-- CARROT:MANUAL:BEGIN LongTuningKpV -->
<!-- CARROT:REVIEW reviewed-for="da83b19cd7c1eaed65e221d1571b66a8f33f00b0c83097c2f56007bccd5323c1" reviewed-at="2026-11-11T05:33:10.288234+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 動作

Ray EV 檢測到 Comma Pedal 且啟用 openpilot 縱向控制後，會顯示 Long Kp/Ki/Kf，並將儲存值用於速度 PID。啟動時讀取儲存值，執行期間約每秒更新一次。

其他現代/起亞/捷尼賽思配置的通用 Kp/Ki/Kf 固定為 1/0/1。豐田/雷克薩斯由專用車輛控制器補償加速度，通用增益固定為 0/0/1。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END LongTuningKpV -->

<!-- CARROT:SETTING:END LongTuningKpV -->
