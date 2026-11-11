<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="VehicleNaviDecelCancel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 原车导航减速中止请求

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancel -->
<a id="VehicleNaviDecelCancel"></a>

## 原车导航减速中止请求

`VehicleNaviDecelCancel`

仅在外部导航未连接时应用（原车导航 CAN）。启用后，在 openpilot 启用（约 18km/h 以上）且下方已启用的类型正在减速时，按一次巡航 + 键或轻踩油门（踩下不足 0.4 秒后松开）即中止该处减速。此输入不会提高设定速度（+1 和轻踩油门 +10 均不生效）。中止只适用于该摄像头或减速带，下一个仍会减速。闯红灯、后向摄像头和区间测速不能中止；固定摄像头仅在其详细项单独开启时可中止。在详细项中按类型（箱式摄像头、移动区间、减速带、固定摄像头）分别开关。

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancel -->
<!-- CARROT:AUTO:SOURCE facts="74ec3b3d3c8371d326fa73af65f800a55a5ca1274065daad466459000e722690" semantic="b4932756ef27f4ad90176e3da43004bb00e3808dc92ffd2bff98e1c48d5fe10f" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancel -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancel -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancel -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancel -->
