<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_TRAFFIC" param="LeadBrakeLights" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 前车制动灯观察（试验）

**菜单:** 驾驶控制 \> 速度与减速 \> 信号灯

---

<!-- CARROT:SETTING:BEGIN LeadBrakeLights -->
<a id="LeadBrakeLights"></a>

## 前车制动灯观察（试验）

`LeadBrakeLights`

默认关闭。开启后仅在信号辅助模式1/2中显示并记录前车中央制动灯候选，不参与减速或起步控制。未检测到不代表灯已关闭。模式0关闭所有辅助处理。

<!-- CARROT:AUTO:BEGIN LeadBrakeLights -->
<!-- CARROT:AUTO:SOURCE facts="af87df5b1b719ee89bf9b0032481ec19f7c68e8b17a72ba46323544e93a6c2e9" semantic="1c52b548b46d979bac0118c3daafe7304a87141b48ac8f9662b240448cd8289a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 信号灯
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadBrakeLights -->

<!-- CARROT:MANUAL:BEGIN LeadBrakeLights -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END LeadBrakeLights -->

<!-- CARROT:SETTING:END LeadBrakeLights -->
