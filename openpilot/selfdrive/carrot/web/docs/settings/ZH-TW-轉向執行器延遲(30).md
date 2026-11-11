<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_FEEL" param="SteerActuatorDelay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 轉向執行器延遲(30)

**選單:** 駕駛控制 \> 轉向 \> 轉向手感

---

<!-- CARROT:SETTING:BEGIN SteerActuatorDelay -->
<a id="SteerActuatorDelay"></a>

## 轉向執行器延遲(30)

`SteerActuatorDelay`

轉向響應延遲補償：30=0.30秒，0=LiveDelay。數值越大，提前補償越多。 重心比例也會影響入彎，比較時保持SAD和SR不變。

<!-- CARROT:AUTO:BEGIN SteerActuatorDelay -->
<!-- CARROT:AUTO:SOURCE facts="e2f3797bd995eeff658656473067d68b22ef136492a94c5d04d961817af6e001" semantic="2d1e59de8edc91af92b92e8bcb989bbc50e68cca9731d896bd7f990032ce4097" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `30`
- **範圍:** `0` ~ `300`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 轉向手感
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SteerActuatorDelay -->

<!-- CARROT:MANUAL:BEGIN SteerActuatorDelay -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END SteerActuatorDelay -->

<!-- CARROT:SETTING:END SteerActuatorDelay -->
