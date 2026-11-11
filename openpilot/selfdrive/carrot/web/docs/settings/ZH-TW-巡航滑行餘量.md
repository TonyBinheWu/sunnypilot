<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_CARROT" param="CruiseCoastingPercent" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 巡航滑行餘量

**選單:** 駕駛控制 \> 巡航與車距 \> Carrot巡航

---

<!-- CARROT:SETTING:BEGIN CruiseCoastingPercent -->
<a id="CruiseCoastingPercent"></a>

## 巡航滑行餘量

`CruiseCoastingPercent`

0%保持原有控制。在超過設定速度時減弱巡航減速，接近餘量上限時恢復減速。不提高設定速度，也不關閉SCC。僅在無前車、停車或外部速度控制介入的普通巡航中生效。

<!-- CARROT:AUTO:BEGIN CruiseCoastingPercent -->
<!-- CARROT:AUTO:SOURCE facts="078464794d318ad3e1d646e731eec4bd1034a7c64bb628beb1178f6c271eef5f" semantic="9e7ec0cc19d4be87699aad493790df42abd5125510f4ee68a4722b620c403b7a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0%`
- **範圍:** `0%` ~ `10%`
- **步長:** `1`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 巡航與車距 \> Carrot巡航
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseCoastingPercent -->

<!-- CARROT:MANUAL:BEGIN CruiseCoastingPercent -->
<!-- CARROT:REVIEW reviewed-for="9e7ec0cc19d4be87699aad493790df42abd5125510f4ee68a4722b620c403b7a" reviewed-at="2026-09-25T08:35:39+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

僅在普通巡航超過設定速度時減弱減速指令。提高此值會擴大允許超速的區間，降低此值會更早恢復正常減速。

- 區間前10%逐漸增加滑行餘量，最後40%逐漸恢復正常減速。不提高設定速度或MPC目標，也不關閉SCC。
- 要求基準速度超過10km/h，設定速度、餘量設定及允許條件保持一秒。進入允許條件時固定換算後的基準速度；之後速度換算比例的變化不會重置等待時間或移動基準。
- 前車、切入候選、停車、彎道限制、外部速度控制、變道及實驗模式均禁止滑行補償。設定速度或餘量改變、或允許條件解除後，需要重新確定基準並等待一秒。
- 節能控制提高目標速度期間及現有CarrotCruise加速限制模式中不生效。導航限速不高於滑行上限時也不生效。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

執行期間約每秒讀取一次設定。選擇關閉值可恢復原有巡航減速控制。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

設定速度100km/h、餘量5%時，在103至105km/h之間恢復正常減速。此功能不會主動加速至105km/h，也不保證實際速度絕不超過上限。

SCC零加速度請求仍可能產生能量回收，具體取決於車輛。尚未完成實車行駛驗證。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseCoastingPercent -->

<!-- CARROT:SETTING:END CruiseCoastingPercent -->
