<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_CANFD" param="HDPuse" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 使用 HDP (CCNC)

**選單:** 車輛與硬體 \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN HDPuse -->
<a id="HDPuse"></a>

## 使用 HDP (CCNC)

`HDPuse`

1: 使用 APN 時, 2: 始終

<!-- CARROT:AUTO:BEGIN HDPuse -->
<!-- CARROT:AUTO:SOURCE facts="653c630cafcdbb7bc7d16b55f53172e1b7dd421ad567c91f3079adca38d38229" semantic="81f1a1ef230e556daa86169f16be0dde67d63f336598dd28620fff74b35b9139" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 車輛與硬體 \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HDPuse -->

<!-- CARROT:MANUAL:BEGIN HDPuse -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- `0` — 停用 HDP 訊息行為。
- `1` — 僅在 APN 啟用時使用 HDP 行為。
- `2` — 持續使用 HDP 行為。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

確認車輛的 HDA 及 CAN FD 配置，停妥後設定，並於下次行車檢查相關功能及故障訊息。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 未經驗證的 CAN FD 配置，可能造成車輛警告或 CAN 故障。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HDPuse -->

<!-- CARROT:SETTING:END HDPuse -->
