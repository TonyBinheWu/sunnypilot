<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_GAP" param="SpeedTFFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 速度 TF 倍率

**選單:** 駕駛控制 \> 巡航與車距 \> 車距

---

<!-- CARROT:SETTING:BEGIN SpeedTFFactor -->
<a id="SpeedTFFactor"></a>

## 速度 TF 倍率

`SpeedTFFactor`

100km/h 時的 TF 倍率：10=1.0倍（不變），20=2.0倍。停車時為1.0倍，隨車速線性增加。不改變跟車響應性。

<!-- CARROT:AUTO:BEGIN SpeedTFFactor -->
<!-- CARROT:AUTO:SOURCE facts="da67033c06ebf551ec7e17cae6340899288fff9be0bc9a357954063f19393a02" semantic="5a06220209167170871cd56a8bbad19e3a0ee27e7de4e1e4e83b573a1dc6126a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** 1.0× (`10`)
- **範圍:** 1.0× (`10`) ~ 3.0× (`30`)
- **步長:** `1`
- **選項:** `10` 1.0×, `11` 1.1×, `12` 1.2×, `13` 1.3×, `14` 1.4×, `15` 1.5×, `16` 1.6×, `17` 1.7×, `18` 1.8×, `19` 1.9×, `20` 2.0×, `21` 2.1×, `22` 2.2×, `23` 2.3×, `24` 2.4×, `25` 2.5×, `26` 2.6×, `27` 2.7×, `28` 2.8×, `29` 2.9×, `30` 3.0×
- **選單:** 駕駛控制 \> 巡航與車距 \> 車距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SpeedTFFactor -->

<!-- CARROT:MANUAL:BEGIN SpeedTFFactor -->
<!-- CARROT:REVIEW reviewed-for="84e34b1b5a1f71494a36b091cec0a6993009fc835fe70f30e264bd5cbe6db98b" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

數值越高，相同車速下的基本TF增加越多。停車時保持基本TF，超過100km/h後仍以相同斜率增加。不改變前車響應級別。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

設為20、基本TF為0.50秒時，0/50/100km/h對應0.50/0.75/1.00秒，再應用駕駛模式及減速修正。舊EnableSpeedTF值不轉換為新設定。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END SpeedTFFactor -->

<!-- CARROT:SETTING:END SpeedTFFactor -->
