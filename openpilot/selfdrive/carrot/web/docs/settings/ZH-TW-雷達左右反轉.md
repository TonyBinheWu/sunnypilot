<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_RADAR" param="RadarTrackFlip" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 雷達左右反轉

**選單:** 車輛與硬體 \> 雷達

---

<!-- CARROT:SETTING:BEGIN RadarTrackFlip -->
<a id="RadarTrackFlip"></a>

## 雷達左右反轉

`RadarTrackFlip`

校正前雷達軌跡的左右方向。 0：正常（預設） 1：反轉橫向位置和橫向速度 不適用於 SCC、角雷達或視覺。同時影響前車選擇和雷達顯示。不按車型自動反轉；僅在確認左右不一致後選擇。更改後請重新啟動車輛或裝置。

<!-- CARROT:AUTO:BEGIN RadarTrackFlip -->
<!-- CARROT:AUTO:SOURCE facts="98a78bf2b153f3b7e541d291e920dd827abff1866ba05df68a5fb895ba87823a" semantic="943dbe7612241b525566748d4a0c0383a19f20e4a140a100fad0a061f818df64" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 正常 (`0`)
- **範圍:** 正常 (`0`) ~ 左右反轉 (`1`)
- **步長:** `1`
- **選項:** `0` 正常, `1` 左右反轉
- **選單:** 車輛與硬體 \> 雷達
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END RadarTrackFlip -->

<!-- CARROT:MANUAL:BEGIN RadarTrackFlip -->
<!-- CARROT:REVIEW reviewed-for="bd236f17fd9177f84d830907b23c61d75e1e8216aac4ca4dfb3cc9e3d4460cb8" reviewed-at="2026-09-23T00:19:35.952962+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

正常模式保留前雷達軌跡座標；反轉模式同時反轉橫向位置和橫向速度。它影響前車選擇和雷達顯示，不改變 SCC、角雷達、視覺及縱向距離和速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

僅在確認影片與雷達左右不一致後選擇反轉。不會按車型自動反轉；更改後請重新啟動車輛或裝置，在下一次 OnRoad 啟動時生效。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END RadarTrackFlip -->

<!-- CARROT:SETTING:END RadarTrackFlip -->
