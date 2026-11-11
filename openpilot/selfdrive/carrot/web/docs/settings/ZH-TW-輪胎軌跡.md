<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_PATH" param="CarrotTireTrajectory" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 輪胎軌跡

**選單:** 顯示 \> 路徑顯示

---

<!-- CARROT:SETTING:BEGIN CarrotTireTrajectory -->
<a id="CarrotTireTrajectory"></a>

## 輪胎軌跡

`CarrotTireTrajectory`

在預測路徑上以漸變色(綠→紅)顯示車道偏離程度, 並在底部顯示偏移量(L/R/C, m)。 0:關, 1:開

<!-- CARROT:AUTO:BEGIN CarrotTireTrajectory -->
<!-- CARROT:AUTO:SOURCE facts="9d99f6af9e05ec284aa1f271ff9eef68c5fdcb3c9925f4198d23d68520d7dcd2" semantic="5a96ee68d440c85103f4c4ff1d0ac55cc74ac347d5e3536e424bbf25810c2a34" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 顯示 \> 路徑顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotTireTrajectory -->

<!-- CARROT:MANUAL:BEGIN CarrotTireTrajectory -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 關閉
- `1` — 開啟
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在行車畫面切換巡航及車道模式狀態，確認路徑形狀與顏色依預期改變。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END CarrotTireTrajectory -->

<!-- CARROT:SETTING:END CarrotTireTrajectory -->
