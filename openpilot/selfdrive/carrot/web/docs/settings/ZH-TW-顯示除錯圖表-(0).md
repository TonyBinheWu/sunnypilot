<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_SCREEN" param="ShowPlotMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 顯示除錯圖表 (0)

**選單:** 顯示 \> 資訊顯示

---

<!-- CARROT:SETTING:BEGIN ShowPlotMode -->
<a id="ShowPlotMode"></a>

## 顯示除錯圖表 (0)

`ShowPlotMode`

0:關, 1:加速度, 2:速度+加速度, 3:模型, 4:前車加速度/相對速度, 5:前車加速度/加加速度, 6:轉向, 7:轉角, 8:曲率

<!-- CARROT:AUTO:BEGIN ShowPlotMode -->
<!-- CARROT:AUTO:SOURCE facts="3a50e268f315bd3a9cabef789726a5a6a1f09e313759d06a834f8a98697b3a80" semantic="7f2319fa7171e1573948b028f5354f0764f43be979f51b1511cabb15ab889343" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** `0`
- **範圍:** `0` ~ `8`
- **步長:** `1`
- **選單:** 顯示 \> 資訊顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPlotMode -->

<!-- CARROT:MANUAL:BEGIN ShowPlotMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 關閉
- `1` — 加速
- `2` — 速度＋加速度
- `3` — 模型
- `4` — 前車
- `5` — 前車 2
- `6` — 轉向
- `7` — 轉向 A
- `8` — 曲率
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

檢查行車畫面的配置及可讀性，只啟用需要的資訊。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPlotMode -->

<!-- CARROT:SETTING:END ShowPlotMode -->
