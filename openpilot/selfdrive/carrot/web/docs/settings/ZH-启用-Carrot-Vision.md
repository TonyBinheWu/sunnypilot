<!-- CARROT:GENERATED schema="1" locale="zh" group="VEH_DM" param="CarrotVisionEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 启用 Carrot Vision

**菜单:** 车辆与硬件 \> 驾驶员监控

---

<!-- CARROT:SETTING:BEGIN CarrotVisionEnabled -->
<a id="CarrotVisionEnabled"></a>

## 启用 Carrot Vision

`CarrotVisionEnabled`

启用网页道路影像，支持停车观看。有观看会话时才请求摄像头与专用编码器，结束后释放；独立于驾驶员监控及外部 HUD。 同时使用视频可能增加设备负载。

<!-- CARROT:AUTO:BEGIN CarrotVisionEnabled -->
<!-- CARROT:AUTO:SOURCE facts="cdd60522dda375f45e46989cbe980d16af80588513670a92c2b334db777be5ad" semantic="b2d518e8de1cb65052caf0bf8dd1cad8094210462341bdc7090b9f4156fdff5f" review="current" -->
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
<!-- CARROT:REVIEW reviewed-for="b2d518e8de1cb65052caf0bf8dd1cad8094210462341bdc7090b9f4156fdff5f" reviewed-at="2026-11-13T16:58:12Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

独立于驾驶员监控及外部 HUD，支持行车及停车道路影像。停车时仅在观看会话存在期间请求摄像头与编码器，其他摄像头使用者仍遵循原有条件。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

开启此设置并进入 App 或网页的 Vision。车机更新并重新启动一次后，可继续使用 CarrotAssist 0.2.16，无需运行诊断摄像头程序。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

停车观看不启动驾驶模型、控制或一般行车录像，也不沿用旧行车指引；录像回放保留记录数据。原有电量关机条件不变。旧 DisableDM 影像选择仅迁移一次，不改变驾驶员监控或实验模式。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CarrotVisionEnabled -->

<!-- CARROT:SETTING:END CarrotVisionEnabled -->
