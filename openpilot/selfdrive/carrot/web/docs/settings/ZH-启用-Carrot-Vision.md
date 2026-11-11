<!-- CARROT:GENERATED schema="1" locale="zh" group="VEH_DM" param="CarrotVisionEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 启用 Carrot Vision

**菜单:** 车辆与硬件 \> 驾驶员监控

---

<!-- CARROT:SETTING:BEGIN CarrotVisionEnabled -->
<a id="CarrotVisionEnabled"></a>

## 启用 Carrot Vision

`CarrotVisionEnabled`

独立于驾驶员监控启用网页道路视频，可与外部HUD同时使用。同时使用视频可能增加设备负载。

<!-- CARROT:AUTO:BEGIN CarrotVisionEnabled -->
<!-- CARROT:AUTO:SOURCE facts="13e592d26ddea0d95c7c1d30d3f387000bbe9b0a1dea8fc0de3578970b84a599" semantic="06ceb617dbe739cddd0239009397024736b16a64f730822966da6da92c24437d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** 关闭 (`0`)
- **范围:** 关闭 (`0`) ~ 开启 (`1`)
- **步长:** `1`
- **选项:** `0` 关闭, `1` 开启
- **菜单:** 车辆与硬件 \> 驾驶员监控
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotVisionEnabled -->

<!-- CARROT:MANUAL:BEGIN CarrotVisionEnabled -->
<!-- CARROT:REVIEW reviewed-for="196e1f296cc743239e491c11d519cea88fbf7bde06ad6f1fe40b377fe6758e07" reviewed-at="2026-09-28T07:45:03.024967+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

启用后可使用网页道路视频，关闭后停止。此设置独立于驾驶员监控。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

需要网页道路视频时启用。启用USB仪表盘时无法使用Carrot Vision。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

旧DisableDM的视频选择仅迁移一次到此设置。迁移不会关闭驾驶员监控或开启实验模式。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CarrotVisionEnabled -->

<!-- CARROT:SETTING:END CarrotVisionEnabled -->
