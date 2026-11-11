<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_TRAFFIC" param="LeadBrakeLights" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 前車制動燈觀察（試驗）

**選單:** 駕駛控制 \> 速度與減速 \> 訊號燈

---

<!-- CARROT:SETTING:BEGIN LeadBrakeLights -->
<a id="LeadBrakeLights"></a>

## 前車制動燈觀察（試驗）

`LeadBrakeLights`

預設關閉。開啟後僅在訊號輔助模式1/2中顯示並記錄前車中央制動燈候選，不參與減速或起步控制。未檢測到不代表燈已關閉。模式0關閉所有輔助處理。

<!-- CARROT:AUTO:BEGIN LeadBrakeLights -->
<!-- CARROT:AUTO:SOURCE facts="50771c1a1c4888f2078f42da50be1467094f9c13da7cfe97b101f4b82395d4ff" semantic="1c52b548b46d979bac0118c3daafe7304a87141b48ac8f9662b240448cd8289a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 訊號燈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadBrakeLights -->

<!-- CARROT:MANUAL:BEGIN LeadBrakeLights -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END LeadBrakeLights -->

<!-- CARROT:SETTING:END LeadBrakeLights -->
