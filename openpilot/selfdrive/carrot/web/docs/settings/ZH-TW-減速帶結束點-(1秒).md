<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_BUMP" param="AutoNaviSpeedBumpTime" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 減速帶結束點 (1秒)

**選單:** 駕駛控制 \> 速度與減速 \> 減速帶

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedBumpTime -->
<a id="AutoNaviSpeedBumpTime"></a>

## 減速帶結束點 (1秒)

`AutoNaviSpeedBumpTime`

減速帶結束點 (1秒)

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedBumpTime -->
<!-- CARROT:AUTO:SOURCE facts="7b0ef3d0035f37a3d5c522d9b8ebbf562ecc94090c2403d637d896025c092199" semantic="7de62e4b1a3ae2d0795b55f526653d5513f930033333ce979280f28bc6580ffc" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `1s`
- **範圍:** `1s` ~ `50s`
- **步長:** `1`
- **顯示單位:** `s`
- **選單:** 駕駛控制 \> 速度與減速 \> 減速帶
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedBumpTime -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedBumpTime -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

使用剩餘距離及目前速度，計算減速丘減速完成位置。

- **調高：** 使用減速丘前方距離較遠的減速完成點。
- **調低：** 使用較接近減速丘的目標點。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同減速丘路段確認減速完成位置及通過速度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedBumpTime -->

<!-- CARROT:SETTING:END AutoNaviSpeedBumpTime -->
