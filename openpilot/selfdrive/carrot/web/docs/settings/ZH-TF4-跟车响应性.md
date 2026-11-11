<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_GAP" param="LeadAccelResponseTF4" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF4 跟车响应性

**菜单:** 驾驶控制 \> 巡航与车距 \> 车距

---

<!-- CARROT:SETTING:BEGIN LeadAccelResponseTF4 -->
<a id="LeadAccelResponseTF4"></a>

## TF4 跟车响应性

`LeadAccelResponseTF4`

巡航车距4级的跟车响应性。-1使用通用值，0～5仅应用于此车距级别。可设置相同的基本TF和不同的响应。 先确定通用值或车距专用值，再应用模式限制：节能最高2，安全最高3，普通和高速保留所选值。较低值和0不会提高，也不会改写保存的设置。 额外余量保持条件在TF距离（车速×TF＋停车距离）的1.2倍以内适用，在1.2至1.5倍之间逐步解除，达到1.5倍后无论前车速度如何都会回收余量。 不单独记忆制动开始时的车距，也不在停车后保持该距离。

<!-- CARROT:AUTO:BEGIN LeadAccelResponseTF4 -->
<!-- CARROT:AUTO:SOURCE facts="60c949aafe2e7eb37384bb0749f8e8029e7be91a61f3b0d345eb6f49d2460240" semantic="98a6de3affc56a6d1146a72fe4af4fe954aaf9bca912ea89256434a150b6a595" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** 使用通用值 (`-1`)
- **范围:** 使用通用值 (`-1`) ~ 5 最大跟随（测试） (`5`)
- **步长:** `1`
- **选项:** `-1` 使用通用值, `0` 0 从容跟随, `1` 1 最柔和, `2` 2 平缓跟随, `3` 3 均衡跟随, `4` 4 快速跟随, `5` 5 最大跟随（测试）
- **菜单:** 驾驶控制 \> 巡航与车距 \> 车距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadAccelResponseTF4 -->

<!-- CARROT:MANUAL:BEGIN LeadAccelResponseTF4 -->
<!-- CARROT:REVIEW reviewed-for="86649c8bc61cf3c79e9166987b9b53dcf40b9e0456bbfdf0e5093eb888a42174" reviewed-at="2026-10-05T01:00:23.810402+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

巡航车距4级使用通用响应或单独设置。级别越高跟随越快，越低恢复车距越从容。

确定通用值或车距专用响应后，节能最高2，安全最高3。普通和高速保留所选值，不提高较低值和0，也不改写保存值。

0～4级的额外余量保持受距离范围限制。基准D为车速×基本TF＋设定停车距离，不包括额外余量。

- 不超过1.2D：使用现有保持与回收条件。
- 1.2D至1.5D：逐步降低保持余量和补充速度，并放宽低速回收限制。
- 达到1.5D：即使前车正在远离或已经停止，也按所选级别的速度回收余量。

不会立即清空余量或直接增加加速度。基本TF、停车距离、制动限制及5级不增加额外余量的规则保持不变。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

两个车距级别可使用相同基本TF和不同响应。加速增强与额外车距恢复使用同一响应值，并保留速度TF倍率。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LeadAccelResponseTF4 -->

<!-- CARROT:SETTING:END LeadAccelResponseTF4 -->
