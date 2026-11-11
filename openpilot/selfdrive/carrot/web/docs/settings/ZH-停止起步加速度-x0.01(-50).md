<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_STOPGO" param="StoppingAccel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 停止起步加速度 x0.01(-50)

**菜单:** 驾驶控制 \> 巡航与车距 \> 停车与再起步

---

<!-- CARROT:SETTING:BEGIN StoppingAccel -->
<a id="StoppingAccel"></a>

## 停止起步加速度 x0.01(-50)

`StoppingAccel`

调整停止控制的加速度进入阈值和减速目标。仅可设置-100至-50；-50代表-0.50m/s²。数值越负，减速目标越强。已有更强的制动请求保持不变，软保持使用车型的停车保持加速度。修改约一秒内生效，行驶中也适用。 现代/起亚 CANFD 的 openpilot 纵向控制从 StopReq 首帧起将 aReqRaw 和 aReqValue 置零，因此保持 StopReq 时本设置不改变发送的加速度。已移除自动释放和重试。

<!-- CARROT:AUTO:BEGIN StoppingAccel -->
<!-- CARROT:AUTO:SOURCE facts="21b87831ceaf67a1b6a3f4376c5afe3862919526b26a62417ed9184ed6ba8398" semantic="804fd76b953b107e414ad27b3ef47d2d75140f0fd06273972f700c8ec2f23490" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `-50`
- **范围:** `-100` ~ `-50`
- **步长:** `10`
- **菜单:** 驾驶控制 \> 巡航与车距 \> 停车与再起步
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END StoppingAccel -->

<!-- CARROT:MANUAL:BEGIN StoppingAccel -->
<!-- CARROT:REVIEW reviewed-for="8cf920bceda9af4842b28a0d610b27791e27425bd798ac75bc1decc6eb97aa48" reviewed-at="2026-09-23T12:54:16+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

**调高（负值减小）：** 减弱减速目标，并延后通常以加速度为条件的停止控制切换。

**调低（负值增大）：** 增强减速目标并提前切换，可能增加停车冲击。已有更强的减速请求保持不变；软保持使用车型的停车保持加速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

修改约一秒内生效，行驶中也适用。停车过程中改为较弱目标，不会立即减弱已经达到的更强制动输出。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

存储值乘以0.01得到m/s²。控制代码也会限制设置范围。原车ACC纵向控制不直接使用此设置；CANFD停止重试无需单独开关，继续生效。参见[停车与再起步指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md#stop-resume)。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END StoppingAccel -->

<!-- CARROT:SETTING:END StoppingAccel -->
