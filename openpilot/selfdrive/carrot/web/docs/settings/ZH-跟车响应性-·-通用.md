<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_GAP" param="LeadAccelResponse" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 跟车响应性 · 通用

**菜单:** 驾驶控制 \> 巡航与车距 \> 车距

---

<!-- CARROT:SETTING:BEGIN LeadAccelResponse -->
<a id="LeadAccelResponse"></a>

## 跟车响应性 · 通用

`LeadAccelResponse`

车距级别选择使用通用值时应用。级别越低越从容，越高响应越快。0关闭加速增强，5为最大响应。所有响应级别均应用速度TF。 先确定通用值或车距专用值，再应用模式限制：节能最高2，安全最高3，普通和高速保留所选值。较低值和0不会提高，也不会改写保存的设置。 额外余量保持条件在TF距离（车速×TF＋停车距离）的1.2倍以内适用，在1.2至1.5倍之间逐步解除，达到1.5倍后无论前车速度如何都会回收余量。 不单独记忆制动开始时的车距，也不在停车后保持该距离。

<!-- CARROT:AUTO:BEGIN LeadAccelResponse -->
<!-- CARROT:AUTO:SOURCE facts="6f7c446e676e347cb38234975783affc921168dd2fa026f87bc316c292918b00" semantic="46d9ff7041e6f7680369b13cd90e72cfa05423b6ad5dbae8d537cadcb8858d89" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** 0 从容跟随 (`0`)
- **范围:** 0 从容跟随 (`0`) ~ 5 最大跟随（测试） (`5`)
- **步长:** `1`
- **选项:** `0` 0 从容跟随, `1` 1 最柔和, `2` 2 平缓跟随, `3` 3 均衡跟随, `4` 4 快速跟随, `5` 5 最大跟随（测试）
- **菜单:** 驾驶控制 \> 巡航与车距 \> 车距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadAccelResponse -->

<!-- CARROT:MANUAL:BEGIN LeadAccelResponse -->
<!-- CARROT:REVIEW reviewed-for="642da0e45e37822a53a84280a2fa8db34ece932cf62dd49a24ca1d9ba737377a" reviewed-at="2026-10-05T01:00:23.824710+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

应用于选择使用通用值的巡航车距级别。级别越低恢复越从容，越高跟随越快，同时调整加速增强和额外车距恢复。

确定通用值或车距专用响应后，节能最高2，安全最高3。普通和高速保留所选值，不提高较低值和0，也不改写保存值。

0～4级的额外余量保持受距离范围限制。基准D为车速×基本TF＋设定停车距离，不包括额外余量。

- 不超过1.2D：使用现有保持与回收条件。
- 1.2D至1.5D：逐步降低保持余量和补充速度，并放宽低速回收限制。
- 达到1.5D：即使前车正在远离或已经停止，也按所选级别的速度回收余量。

不会立即清空余量或直接增加加速度。基本TF、停车距离、制动限制及5级不增加额外余量的规则保持不变。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

所有响应级别均基于速度倍率和驾驶模式修正后的TF。已移除4～5级跳过速度TF的特例。保留必要制动及现有加速限制。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LeadAccelResponse -->

<!-- CARROT:SETTING:END LeadAccelResponse -->
