<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_FEEL" param="LatSuspendAngleDeg" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AutoSteering Suspend Angle(300)

**選單:** 駕駛控制 \> 轉向 \> 轉向手感

---

<!-- CARROT:SETTING:BEGIN LatSuspendAngleDeg -->
<a id="LatSuspendAngleDeg"></a>

## AutoSteering Suspend Angle(300)

`LatSuspendAngleDeg`

Auto steering pauses at large steering angles and resumes when it returns within 15.

<!-- CARROT:AUTO:BEGIN LatSuspendAngleDeg -->
<!-- CARROT:AUTO:SOURCE facts="09c59744e096a6dd4d0cd5586eeff4431bf04414ce65142989ba2f3d927d621c" semantic="6a5eddcf99410a800bf67cddd5eed9ce00f5be22d98b8e33bcfaec45e132a42b" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `300`
- **範圍:** `45` ~ `300`
- **步長:** `10`
- **選單:** 駕駛控制 \> 轉向 \> 轉向手感
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatSuspendAngleDeg -->

<!-- CARROT:MANUAL:BEGIN LatSuspendAngleDeg -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

大轉向角時暫停自動轉向，回到 15 以內後恢復。

- **調高：** 駕駛介入轉向時，達到較大的轉向角度才會暫停輔助轉向。
- **調低：** 在較小的轉向角度就會較早暫停輔助轉向。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同直路及平緩彎道，每次小幅調整一項，檢查延遲、振盪及駕駛介入後的恢復。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 不適當的數值可能降低轉向或縱向控制的穩定性與舒適度。每次只小幅調整一項，行為異常時恢復預設值。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LatSuspendAngleDeg -->

<!-- CARROT:SETTING:END LatSuspendAngleDeg -->
