<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_SCREEN" param="ShowPlotMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 디버그플롯(0)

**메뉴:** 화면 표시 \> 정보 표시

---

<!-- CARROT:SETTING:BEGIN ShowPlotMode -->
<a id="ShowPlotMode"></a>

## 디버그플롯(0)

`ShowPlotMode`

0: 끄기, 1: 가속도, 2: 속도+가속도, 3: 모델, 4: 앞차 가속도·상대속도, 5: 앞차 가속도·저크, 6: Steer, 7: SteerA, 8: Curvature

<!-- CARROT:AUTO:BEGIN ShowPlotMode -->
<!-- CARROT:AUTO:SOURCE facts="0912c897bad4a854f631e764a130775c6706b25d9d7374687d375bb241e0b227" semantic="7f2319fa7171e1573948b028f5354f0764f43be979f51b1511cabb15ab889343" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** `0`
- **범위:** `0` ~ `8`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 정보 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPlotMode -->

<!-- CARROT:MANUAL:BEGIN ShowPlotMode -->
<!-- CARROT:REVIEW reviewed-for="fed9a1ccaab19da852200d90359bf75c4ff2d2c99e35ed39b63cfd57c001b853" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 끄기
- `1` — 가속도
- `2` — 속도+가속도
- `3` — 모델
- `4` — Lead
- `5` — Lead2
- `6` — Steer
- `7` — SteerA
- `8` — Curvature
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 화면에서 정보의 위치와 가독성을 확인하고, 필요한 정보만 표시되도록 선택합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPlotMode -->

<!-- CARROT:SETTING:END ShowPlotMode -->
