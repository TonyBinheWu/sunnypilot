<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_FEEL" param="HkgPhase1Assist" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 现代起亚四车系转向与弯道辅助

**菜单:** 驾驶控制 \> 转向 \> 转向手感

---

<!-- CARROT:SETTING:BEGIN HkgPhase1Assist -->
<a id="HkgPhase1Assist"></a>

## 现代起亚四车系转向与弯道辅助

`HkgPhase1Assist`

仅限已登记的 EV6、Ioniq 5、Carnival、Sorento 平台。CAN-FD 力矩车型沿用低速需求跟随（最高 409、4/4），保留已存手动值；角度控制及旧款 Sorento 保持原执行器限制。40–80 km/h 逐渐平滑小幅曲率修正，大幅需求减少滤波。直接纵向 ACC 模式下，以连续三个新鲜模型帧确认前方弯道，再降低 MPC 速度上限。默认关闭，保留 EPS/Panda 保护；不包含紧急避让，不保证迴转或实车效果。 低速同方向入弯需求将既有目标滤波时间常数最多缩短 40%；回正与反向维持原滤波，30–40 km/h 渐退。 低速模型目标反应调整仅用于无车道线模型路径；自定义车道线规划滤波及其延迟补偿保持不变。 使用 ADAS ECU 的 EV6 HDA2 扭矩转向在开启任一功能时仍采用专用两段上限和受限增减速率，可记录转向响应。

<!-- CARROT:AUTO:BEGIN HkgPhase1Assist -->
<!-- CARROT:AUTO:SOURCE facts="7050dc2baa91a6fe118a80123d3693550dc1bf00c5e0e3da020813b30939f825" semantic="0e6f0cdf4d784a5157f3298eeadcb01f00db7ae44d927282eb756eaab2599891" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> 转向手感
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HkgPhase1Assist -->

<!-- CARROT:MANUAL:BEGIN HkgPhase1Assist -->
<!-- CARROT:REVIEW reviewed-for="1c9c7c054bb743a7a9af0906faec089755f21f0f914e02d4a5b7addd3c56d7c2" reviewed-at="2026-11-18T00:00:00+08:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 运作方式

仅套用已登录的 EV6、Ioniq 5、Carnival、Sorento 平台，维持既有车型、HDA 与扭力／角度辨识。低速同方向增大的入弯需求，将既有目标滤波时间常数最多缩短 40%，30–40 km/h 渐退；回正与反向使用原滤波。CAN-FD 扭力车型另沿用 LowSpeedSteerReserve 的资格确认、扭力上限与速率保护。角度车型与旧款 Sorento 不增加执行器权限。高速小幅曲率修正增加最多 0.08 秒时间常数的滤波，大幅需求减少滤波，最终曲率与执行器限制仍生效。
低速模型目标反应调整仅用于无车道线模型路径；自定义车道线规划滤波及其延迟补偿保持不变。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

停妥后在驾驶控制 > 转向 > 转向手感启用，逐一验证各车配置。转向约 0.5 秒、弯道辅助约 1 秒读取设定；本开关与 LowSpeedSteerReserve 都关闭后才恢复手动限制，储存值不被覆写。既有低速扭力路径仍须相容 Panda 韧体。仅在 ACC 模式、直接纵向与横向控制皆启用、车辆／控制／模型资料有效并连续三个新模型帧确认后，套用弯前速度上限；原厂 ACC 与 blended 模式不变。使用模型前方最多 4 秒几何、2.0 m/s² 横向舒适目标与 1.2 m/s² 接近减速预算；上限每秒最多下降 1.2 m/s、每秒回升 0.5 m/s。在 Carrot 选速之后交给 MPC，不提高较低速度或停车目标，也不让滑行与前车加速预览抵销弯道减速。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 补充说明

驾驶踏板／转向介入、CAN 无效、转向故障、控制退出、模型过期／重复／重启或几何异常会重置弯道上限。新增弯道功能不要求停车，不以观察纪录推定 EPS 能力。维持 EPS／Panda 保护、驾驶优先、请求位元防故障、模型档与紧急行为。桌面测试不能证明实车操控效果、满舵／回转能力或与 FSD 等效。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END HkgPhase1Assist -->

<!-- CARROT:SETTING:END HkgPhase1Assist -->
