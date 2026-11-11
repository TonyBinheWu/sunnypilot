<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_FEEL" param="CenterToFrontRatio" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 重心位置比例

**菜单:** 驾驶控制 \> 转向 \> 转向手感

---

<!-- CARROT:SETTING:BEGIN CenterToFrontRatio -->
<a id="CenterToFrontRatio"></a>

## 重心位置比例

`CenterToFrontRatio`

0=车型默认值，其他值31~69%=轴距×比例。保存后平滑生效，无需重启。 默认：现代/起亚/捷尼赛思40%，丰田/雷克萨斯44%，马自达41%，大众45%，本田因车型而异。 入弯偏晚可小幅增加，入弯切向内侧可小幅减小；效果因车道模式和车辆而异。 保持SAD和SR不变，一次只调一项。变差时恢复原值或0。

<!-- CARROT:AUTO:BEGIN CenterToFrontRatio -->
<!-- CARROT:AUTO:SOURCE facts="0c3cc16f8866eeaf794520db690539f2944c51f45cc3d9d0d5f3d8329b770e09" semantic="ffcefcd7552894afdf0dbf200567b02117bac3fdd8a60a8f29a28907d3976f52" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0%`
- **范围:** `0%` ~ `69%`
- **步长:** `1`
- **显示单位:** `%`
- **菜单:** 驾驶控制 \> 转向 \> 转向手感
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CenterToFrontRatio -->

<!-- CARROT:MANUAL:BEGIN CenterToFrontRatio -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CenterToFrontRatio -->

<!-- CARROT:SETTING:END CenterToFrontRatio -->
