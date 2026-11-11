<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_STOPGO" param="StoppingAccel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 停止起步加速度 x0.01(-50)

**選單:** 駕駛控制 \> 巡航與車距 \> 停車與再起步

---

<!-- CARROT:SETTING:BEGIN StoppingAccel -->
<a id="StoppingAccel"></a>

## 停止起步加速度 x0.01(-50)

`StoppingAccel`

調整停止控制的加速度進入閾值和減速目標。僅可設定-100至-50；-50代表-0.50m/s²。數值越負，減速目標越強。已有更強的制動請求保持不變，軟保持使用車型的停車保持加速度。修改約一秒內生效，行駛中也適用。 現代/起亞 CANFD 的 openpilot 縱向控制從 StopReq 首幀起將 aReqRaw 和 aReqValue 置零，因此保持 StopReq 時本設定不改變傳送的加速度。已移除自動釋放和重試。

<!-- CARROT:AUTO:BEGIN StoppingAccel -->
<!-- CARROT:AUTO:SOURCE facts="213f4252088de4f4d9fd5cba7b7af49675e926c2b775c5a6b08fcb573a3f9d85" semantic="804fd76b953b107e414ad27b3ef47d2d75140f0fd06273972f700c8ec2f23490" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `-50`
- **範圍:** `-100` ~ `-50`
- **步長:** `10`
- **選單:** 駕駛控制 \> 巡航與車距 \> 停車與再起步
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END StoppingAccel -->

<!-- CARROT:MANUAL:BEGIN StoppingAccel -->
<!-- CARROT:REVIEW reviewed-for="8cf920bceda9af4842b28a0d610b27791e27425bd798ac75bc1decc6eb97aa48" reviewed-at="2026-09-23T12:54:16+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

**調高（負值減小）：** 減弱減速目標，並延後通常以加速度為條件的停止控制切換。

**調低（負值增大）：** 增強減速目標並提前切換，可能增加停車衝擊。已有更強的減速請求保持不變；軟保持使用車型的停車保持加速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

修改約一秒內生效，行駛中也適用。停車過程中改為較弱目標，不會立即減弱已經達到的更強制動輸出。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

儲存值乘以0.01得到m/s²。控制程式碼也會限制設定範圍。原車ACC縱向控制不直接使用此設定；CANFD停止重試無需單獨開關，繼續生效。參見[停車與再起步指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md#stop-resume)。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END StoppingAccel -->

<!-- CARROT:SETTING:END StoppingAccel -->
