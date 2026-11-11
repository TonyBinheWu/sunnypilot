<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SYS_CAMERA" param="UseWideCamera" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 使用廣角前置攝影機

**選單:** 系統 \> 攝影機

---

<!-- CARROT:SETTING:BEGIN UseWideCamera -->
<a id="UseWideCamera"></a>

## 使用廣角前置攝影機

`UseWideCamera`

預設開啟。僅在廣角前置攝影機故障的裝置上關閉。關閉後，camerad 會將廣角攝影機排除在同步之外，modeld 會將普通前置攝影機畫面複用於兩個模型輸入。攝像範圍和模型效能可能會變化。更改後請重新啟動裝置。

<!-- CARROT:AUTO:BEGIN UseWideCamera -->
<!-- CARROT:AUTO:SOURCE facts="550a8a62628e5be7ab4a6a94226aac210970cf0d499f4005b2da60b6ff2dfb46" semantic="98f6143429525738b1a1748e10af5089802e78c1eeeb632ec050ee74ca08fd18" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `1`
- **範圍:** `0` ~ `1`
- **選單:** 系統 \> 攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END UseWideCamera -->

<!-- CARROT:MANUAL:BEGIN UseWideCamera -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END UseWideCamera -->

<!-- CARROT:SETTING:END UseWideCamera -->
