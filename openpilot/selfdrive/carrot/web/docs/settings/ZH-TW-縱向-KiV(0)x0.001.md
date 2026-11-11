<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_LONGTUNE" param="LongTuningKiV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 縱向 KiV(0)x0.001

**選單:** 駕駛控制 \> 巡航與車距 \> 加減速調校

---

<!-- CARROT:SETTING:BEGIN LongTuningKiV -->
<a id="LongTuningKiV"></a>

## 縱向 KiV(0)x0.001

`LongTuningKiV`

縱向控制積分增益。現代、起亞和捷尼賽思的一般縱向控制固定為 Ki 0，因此不會顯示或應用此設定。 豐田/雷克薩斯的通用 Ki=0 固定，以避免與專用控制器重複補償；此設定隱藏且不應用儲存值。 已識別為 Ray EV Comma Pedal 控制時顯示此設定，並在約一秒內將儲存值應用於速度 PID。 實際 Ki 為儲存值乘以 0.001。

<!-- CARROT:AUTO:BEGIN LongTuningKiV -->
<!-- CARROT:AUTO:SOURCE facts="118ab848846e44858d9e5bd448c35473a202dcd867b23bcd80733911afc4d30e" semantic="408a16f2cac3b273bfca7a6a8fe50a70b9f2aed1b3ad6042d70f49451eb04700" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `2000`
- **步長:** `1`
- **選單:** 駕駛控制 \> 巡航與車距 \> 加減速調校
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongTuningKiV -->

<!-- CARROT:MANUAL:BEGIN LongTuningKiV -->
<!-- CARROT:REVIEW reviewed-for="408a16f2cac3b273bfca7a6a8fe50a70b9f2aed1b3ad6042d70f49451eb04700" reviewed-at="2026-11-11T05:33:10.295260+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 動作

Ray EV 檢測到 Comma Pedal 且啟用 openpilot 縱向控制後，會顯示 Long Kp/Ki/Kf，並將儲存值用於速度 PID。啟動時讀取儲存值，執行期間約每秒更新一次。

其他現代/起亞/捷尼賽思配置的通用 Kp/Ki/Kf 固定為 1/0/1。豐田/雷克薩斯由專用車輛控制器補償加速度，通用增益固定為 0/0/1。
實際 Ki 係數為儲存值 × 0.001。儲存值 50 對應 0.050，100 對應 0.100。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END LongTuningKiV -->

<!-- CARROT:SETTING:END LongTuningKiV -->
