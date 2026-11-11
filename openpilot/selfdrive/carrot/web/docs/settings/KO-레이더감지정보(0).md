<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_SCREEN" param="ShowRadarInfo" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 레이더감지정보(0)

**메뉴:** 화면 표시 \> 정보 표시

---

<!-- CARROT:SETTING:BEGIN ShowRadarInfo -->
<a id="ShowRadarInfo"></a>

## 레이더감지정보(0)

`ShowRadarInfo`

0: 안함 1: 표시함 2: 상대위치 3: 정지차량

<!-- CARROT:AUTO:BEGIN ShowRadarInfo -->
<!-- CARROT:AUTO:SOURCE facts="3e6b83b8e70b9654fe7b3ed3b52b4755089a2366a449d3b2061fbd64e5cb21b9" semantic="fb6304349c3a0b1cfa84b4b40b7437938cd0f850a9949f10e2c90253a72c5c3d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 정보 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowRadarInfo -->

<!-- CARROT:MANUAL:BEGIN ShowRadarInfo -->
<!-- CARROT:REVIEW reviewed-for="fb6304349c3a0b1cfa84b4b40b7437938cd0f850a9949f10e2c90253a72c5c3d" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 안함
- `1` — 표시함
- `2` — 상대위치
- `3` — 정지차량

ARS 표시 스트림을 지원하는 RAV4 2022의 장치 기본 주행 화면에서는 `3`이 제어용 앞차 목록과 분리한 옆 차선 객체도 표시합니다. 움직이는 객체는 속도, 느린 객체·정지 물체는 별표로 표시하며, 표시된 객체가 제동 대상으로 선택됐다는 뜻은 아닙니다.

CRC·객체 나이·속도 유효성과 거리 조건은 유지하고, 만료·오류·빈 입력에서는 표시를 지웁니다. `1`과 `2`, 다른 수신기, 웹·mici 화면은 기존 경로를 사용하며 Toyota 측면 코너레이더 지원은 추가하지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 화면에서 정보의 위치와 가독성을 확인하고, 필요한 정보만 표시되도록 선택합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowRadarInfo -->

<!-- CARROT:SETTING:END ShowRadarInfo -->
