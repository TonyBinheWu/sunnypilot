<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="AutoNaviSpeedCtrlMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 導航減速模式 (2)

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedCtrlMode -->
<a id="AutoNaviSpeedCtrlMode"></a>

## 導航減速模式 (2)

`AutoNaviSpeedCtrlMode`

0: 不使用, 1: 限速攝影機, 2: 攝影機 + 減速帶, 3: 攝影機 + 減速帶 + APN 限速攝影機 原車導航 CAN（VehicleNaviCanControl）的移動測速區間（導航藍色圓圈）也遵循此值：3 時減速，2 及以下忽略移動區間警告。同一警告中若同時存在固定、闖紅燈或後向攝影機，則始終減速。

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedCtrlMode -->
<!-- CARROT:AUTO:SOURCE facts="476e0acf1580be4af7c3424bd5d8efd1901b56e72db2d6fff0be27015515ab25" semantic="5b13349929a99c31fde786817313f0a97c7480cf55cdbce1da21739b3610e6d5" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `2`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedCtrlMode -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedCtrlMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 不使用
- `1` — 測速攝影機
- `2` — 測速攝影機＋減速丘
- `3` — 測速攝影機＋減速丘＋APN 測速攝影機
支援的原廠導航 CAN 移動式測速區域也遵循此設定：模式 3 減速，2 或以下忽略移動式測速區域警示。若同時有固定式、號誌或後方執法，仍保留減速。

<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同速限及測速照相類型下，每次調整一項，比較減速起點、完成位置及通過速度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 導航資料必須提供所選事件類型的距離與速限資訊，自動減速才會作用。
<!-- CARROT:NOTICE:END -->

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedCtrlMode -->

<!-- CARROT:SETTING:END AutoNaviSpeedCtrlMode -->
