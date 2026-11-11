<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="BlinkerLatchedTurn" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 转向灯拨杆区分转弯/变道 (km/h, 0=关)

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN BlinkerLatchedTurn -->
<a id="BlinkerLatchedTurn"></a>

## 转向灯拨杆区分转弯/变道 (km/h, 0=关)

`BlinkerLatchedTurn`

仅限现代 CAN-FD（0x3C1 拨杆信号）。0 为关闭。设定速度及以下时，先半拨（单触），转向灯亮-灭-亮之后再拨到底（锁定）为左/右转弯；直接锁定或仅单触为变道；拨杆仍在单触位置时不开始变道（锁定前也会经过该位置约 0.1 秒）。超过设定速度时，即使锁定拨杆也只变道。

<!-- CARROT:AUTO:BEGIN BlinkerLatchedTurn -->
<!-- CARROT:AUTO:SOURCE facts="94afd466bb2d112cf21dc88793fc7be0b3c51bfbbec6deee71b0a9ec5076373c" semantic="76514ada656e4e01d74e337bcc01f3dc8948509aca88bc57278eade000b25502" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0km/h`
- **范围:** `0km/h` ~ `80km/h`
- **步长:** `5`
- **显示单位:** `km/h`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END BlinkerLatchedTurn -->

<!-- CARROT:MANUAL:BEGIN BlinkerLatchedTurn -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END BlinkerLatchedTurn -->

<!-- CARROT:SETTING:END BlinkerLatchedTurn -->
