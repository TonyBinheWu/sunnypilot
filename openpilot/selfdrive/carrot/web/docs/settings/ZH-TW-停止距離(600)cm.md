<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_STOPGO" param="StopDistanceCarrot" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 停止距離(600)cm

**選單:** 駕駛控制 \> 巡航與車距 \> 停車與再起步

---

<!-- CARROT:SETTING:BEGIN StopDistanceCarrot -->
<a id="StopDistanceCarrot"></a>

## 停止距離(600)cm

`StopDistanceCarrot`

停止距離 \* 0.8

<!-- CARROT:AUTO:BEGIN StopDistanceCarrot -->
<!-- CARROT:AUTO:SOURCE facts="0bd841b93a245324bc56eaf909455faf5dbfca30245d5cf426d81c9655a5592a" semantic="828f04295b09ba58b2345b32de89023747b2e835cd5f40e45378caea5d4fc7d8" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `600cm`
- **範圍:** `400cm` ~ `1000cm`
- **步長:** `10`
- **顯示單位:** `cm`
- **選單:** 駕駛控制 \> 巡航與車距 \> 停車與再起步
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END StopDistanceCarrot -->

<!-- CARROT:MANUAL:BEGIN StopDistanceCarrot -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

設定縱向 MPC 對前車及停車障礙物使用的基本停車緩衝距離。

- **調高：** 增加目標停車與跟車的預留距離。
- **調低：** 減少目標預留距離。
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
<!-- CARROT:MANUAL:END StopDistanceCarrot -->

<!-- CARROT:SETTING:END StopDistanceCarrot -->
