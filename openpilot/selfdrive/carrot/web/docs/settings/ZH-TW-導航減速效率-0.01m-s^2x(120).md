<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="AutoNaviSpeedDecelRate" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 導航減速效率 0.01m/s^2x(120)

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedDecelRate -->
<a id="AutoNaviSpeedDecelRate"></a>

## 導航減速效率 0.01m/s^2x(120)

`AutoNaviSpeedDecelRate`

用於計算接近攝影機和減速帶時的減速曲線。儲存值乘以 0.01 m/s²，120 表示 1.2 m/s²。數值越低，開始減速的距離越遠；數值越高，開始減速的距離越近。軟體更新不會更改已儲存的設定。

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedDecelRate -->
<!-- CARROT:AUTO:SOURCE facts="a51b46dbadd7df55ef08f8b4671978ed8447f9e95a37f12c03b0ffb48e02b810" semantic="dd424d47dfc026837af962b9c56209e7643717b0eba2e3136437850b8bdd30c3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `120`
- **範圍:** `50` ~ `300`
- **步長:** `10`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedDecelRate -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedDecelRate -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END AutoNaviSpeedDecelRate -->

<!-- CARROT:SETTING:END AutoNaviSpeedDecelRate -->
