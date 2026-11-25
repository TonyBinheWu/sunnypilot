<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_TORQUE_LIMIT" param="CustomSteerMax" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自定义最大转向力矩(0)

**菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制

---

<!-- CARROT:SETTING:BEGIN CustomSteerMax -->
<a id="CustomSteerMax"></a>

## 自定义最大转向力矩(0)

`CustomSteerMax`

最大转向力矩 — 在 270/384/409 中选择不报错的最大值 使用 ADAS ECU 的 EV6 HDA2 扭矩转向在低于 11 m/s 时采用 384，达到 11 m/s 时采用 330。较低的正数设定可限制两段输出。

<!-- CARROT:AUTO:BEGIN CustomSteerMax -->
<!-- CARROT:AUTO:SOURCE facts="f1dee382162722cd53776a37e953550a7e54dbda6e95a610558175d4c4653a02" semantic="69a6e47badf874d2955d531c868fbb567fbe47091875499338aed77993a98279" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0`
- **范围:** `0` ~ `30000`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerMax -->

<!-- CARROT:MANUAL:BEGIN CustomSteerMax -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CustomSteerMax -->

<!-- CARROT:SETTING:END CustomSteerMax -->
