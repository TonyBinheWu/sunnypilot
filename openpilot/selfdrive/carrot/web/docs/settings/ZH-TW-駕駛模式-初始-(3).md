<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_DRIVE_MODE" param="MyDrivingMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 駕駛模式: 初始 (3)

**選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 駕駛模式

---

<!-- CARROT:SETTING:BEGIN MyDrivingMode -->
<a id="MyDrivingMode"></a>

## 駕駛模式: 初始 (3)

`MyDrivingMode`

1: 節能 - 最大加速度×0.9，時間車距×1.1，前車響應最高2。 2: 安全 - 最大加速度×0.8，時間車距×1.2，前車響應最高3，並保留提前平緩減速的餘量。 3: 普通 - 基本加速和車距，使用所選響應。 4: 高速 - 最大加速度×1.2，保留所選響應，禁用紅綠燈停車。 不再疊加模式專用的加加速度調整，模式車距餘量逐漸釋放。較低響應值和0不會提高。

<!-- CARROT:AUTO:BEGIN MyDrivingMode -->
<!-- CARROT:AUTO:SOURCE facts="1e88879efc8f1934e50164dbb095c4111bf86da28f3f2622efadab601e6fb8df" semantic="6405b6142b9c6696548a67a172fbe0c6fcae9520e0055bb628b5ca3647987b6e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `3`
- **範圍:** `1` ~ `4`
- **步長:** `1`
- **選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 駕駛模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MyDrivingMode -->

<!-- CARROT:MANUAL:BEGIN MyDrivingMode -->
<!-- CARROT:REVIEW reviewed-for="6405b6142b9c6696548a67a172fbe0c6fcae9520e0055bb628b5ca3647987b6e" reviewed-at="2026-09-13T10:16:28.802623+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

節能使用最大加速度×0.9、時間車距×1.1。安全使用最大加速度×0.8、時間車距×1.2及平緩停車餘量。普通使用基本值，高速使用最大加速度×1.2並關閉紅綠燈停止和起步檢測。

確定通用值或車距專用響應後，節能最高2，安全最高3。普通和高速保留所選值，不提高較低值和0，也不改寫儲存值。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END MyDrivingMode -->

<!-- CARROT:SETTING:END MyDrivingMode -->
