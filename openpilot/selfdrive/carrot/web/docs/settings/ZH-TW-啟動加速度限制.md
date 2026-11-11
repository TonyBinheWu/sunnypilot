<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_STOPGO" param="AChangeCostStarting" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 啟動加速度限制

**選單:** 駕駛控制 \> 巡航與車距 \> 停車與再起步

---

<!-- CARROT:SETTING:BEGIN AChangeCostStarting -->
<a id="AChangeCostStarting"></a>

## 啟動加速度限制

`AChangeCostStarting`

啟動加速代價，0: 快速啟動

<!-- CARROT:AUTO:BEGIN AChangeCostStarting -->
<!-- CARROT:AUTO:SOURCE facts="adc59dc322e43b4d912b51ba1fee09e4c723a7f11fc16ec2c428e80bb43506bf" semantic="66fd2bf8a16210234cb0ec52d03ef432cc413d2ec880fd815f8fb436da528c88" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `10`
- **範圍:** `0` ~ `200`
- **步長:** `10`
- **選單:** 駕駛控制 \> 巡航與車距 \> 停車與再起步
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AChangeCostStarting -->

<!-- CARROT:MANUAL:BEGIN AChangeCostStarting -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

調整起步時加速度變化的懲罰權重。

- **調高：** 起步時對加速度變化施加較大的抑制。
- **調低：** 允許起步加速更快。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同前車走走停停的條件下，每次調整一項，檢查最終停車位置及重新起步反應。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 不適當的數值可能降低轉向或縱向控制的穩定性與舒適度。每次只小幅調整一項，行為異常時恢復預設值。
<!-- CARROT:NOTICE:END -->

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AChangeCostStarting -->

<!-- CARROT:SETTING:END AChangeCostStarting -->
