<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_GAP" param="SpeedTFFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 速度 TF 倍率

**菜单:** 驾驶控制 \> 巡航与车距 \> 车距

---

<!-- CARROT:SETTING:BEGIN SpeedTFFactor -->
<a id="SpeedTFFactor"></a>

## 速度 TF 倍率

`SpeedTFFactor`

100km/h 时的 TF 倍率：10=1.0倍（不变），20=2.0倍。停车时为1.0倍，随车速线性增加。不改变跟车响应性。

<!-- CARROT:AUTO:BEGIN SpeedTFFactor -->
<!-- CARROT:AUTO:SOURCE facts="73090864e99537002a1125b5fbf13c63ce5b102e68fcb92583855eecafb44c6c" semantic="5a06220209167170871cd56a8bbad19e3a0ee27e7de4e1e4e83b573a1dc6126a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** 1.0× (`10`)
- **范围:** 1.0× (`10`) ~ 3.0× (`30`)
- **步长:** `1`
- **选项:** `10` 1.0×, `11` 1.1×, `12` 1.2×, `13` 1.3×, `14` 1.4×, `15` 1.5×, `16` 1.6×, `17` 1.7×, `18` 1.8×, `19` 1.9×, `20` 2.0×, `21` 2.1×, `22` 2.2×, `23` 2.3×, `24` 2.4×, `25` 2.5×, `26` 2.6×, `27` 2.7×, `28` 2.8×, `29` 2.9×, `30` 3.0×
- **菜单:** 驾驶控制 \> 巡航与车距 \> 车距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SpeedTFFactor -->

<!-- CARROT:MANUAL:BEGIN SpeedTFFactor -->
<!-- CARROT:REVIEW reviewed-for="84e34b1b5a1f71494a36b091cec0a6993009fc835fe70f30e264bd5cbe6db98b" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

数值越高，相同车速下的基本TF增加越多。停车时保持基本TF，超过100km/h后仍以相同斜率增加。不改变前车响应级别。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

设为20、基本TF为0.50秒时，0/50/100km/h对应0.50/0.75/1.00秒，再应用驾驶模式及减速修正。旧EnableSpeedTF值不转换为新设置。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END SpeedTFFactor -->

<!-- CARROT:SETTING:END SpeedTFFactor -->
