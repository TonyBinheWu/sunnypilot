<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_COEFF" param="NNFF" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# NNFF 扭矩控制

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數

---

<!-- CARROT:SETTING:BEGIN NNFF -->
<a id="NNFF"></a>

## NNFF 扭矩控制

`NNFF`

用於扭矩轉向的神經網路前饋選項。開啟後，非轉角控制車輛使用扭矩控制調校，並在有匹配模型時應用 NNFF。支援 comma 自有 NNFF 的車型仍優先使用原有路徑。關閉僅停用此 NNFF 選項，不改變 NNFFLite。預設關閉，僅在 Carrot Web 搜尋中顯示。更改在下次進入行車模式或裝置重新啟動後生效。不適用於轉角控制車輛。

<!-- CARROT:AUTO:BEGIN NNFF -->
<!-- CARROT:AUTO:SOURCE facts="4f9ce02bcf0dd57b7009a10dec2822d1718989bb07820ee01e4eee7226b4960f" semantic="bf1b67050f021288a3be062698bf0689878aedc8c326f0f30176feec716d40f2" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END NNFF -->

<!-- CARROT:MANUAL:BEGIN NNFF -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END NNFF -->

<!-- CARROT:SETTING:END NNFF -->
