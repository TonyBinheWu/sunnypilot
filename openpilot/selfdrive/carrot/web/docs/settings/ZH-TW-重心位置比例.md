<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_FEEL" param="CenterToFrontRatio" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 重心位置比例

**選單:** 駕駛控制 \> 轉向 \> 轉向手感

---

<!-- CARROT:SETTING:BEGIN CenterToFrontRatio -->
<a id="CenterToFrontRatio"></a>

## 重心位置比例

`CenterToFrontRatio`

0=車型預設值，其他值31~69%=軸距×比例。儲存後平滑生效，無需重新啟動。 預設：現代/起亞/捷尼賽思40%，豐田/雷克薩斯44%，馬自達41%，大眾45%，本田因車型而異。 入彎偏晚可小幅增加，入彎切向內側可小幅減小；效果因車道模式和車輛而異。 保持SAD和SR不變，一次只調一項。變差時恢復原值或0。

<!-- CARROT:AUTO:BEGIN CenterToFrontRatio -->
<!-- CARROT:AUTO:SOURCE facts="f7c2fd1b855b8cace2484739fae2272dad6144ded985519f62c3633ab50f6027" semantic="ffcefcd7552894afdf0dbf200567b02117bac3fdd8a60a8f29a28907d3976f52" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0%`
- **範圍:** `0%` ~ `69%`
- **步長:** `1`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 轉向 \> 轉向手感
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CenterToFrontRatio -->

<!-- CARROT:MANUAL:BEGIN CenterToFrontRatio -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CenterToFrontRatio -->

<!-- CARROT:SETTING:END CenterToFrontRatio -->
