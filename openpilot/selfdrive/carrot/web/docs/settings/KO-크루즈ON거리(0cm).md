<!-- CARROT:GENERATED schema="1" locale="ko" group="BASIC_AUTOCRUISE" param="CruiseOnDist" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 크루즈ON거리(0cm)

**메뉴:** 주행 제어 \> 시작·오토 \> 오토크루즈

---

<!-- CARROT:SETTING:BEGIN CruiseOnDist -->
<a id="CruiseOnDist"></a>

## 크루즈ON거리(0cm)

`CruiseOnDist`

페달을 땠을 때, 앞차가 가까워지면 크루즈ON

<!-- CARROT:AUTO:BEGIN CruiseOnDist -->
<!-- CARROT:AUTO:SOURCE facts="2f06c5f171c032a43329c89ec1a65f3b57fd9d135a53084ad2039047fc8a52b3" semantic="0c44a52dc53d02fb2b5c312b7ff88bdfab957c811fecd2c138ecd67868f032bb" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0cm`
- **범위:** `0cm` ~ `2500cm`
- **변경 단위:** `50`
- **표시 단위:** `cm`
- **메뉴:** 주행 제어 \> 시작·오토 \> 오토크루즈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseOnDist -->

<!-- CARROT:MANUAL:BEGIN CruiseOnDist -->
<!-- CARROT:REVIEW reviewed-for="0c44a52dc53d02fb2b5c312b7ff88bdfab957c811fecd2c138ecd67868f032bb" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

페달을 땠을 때, 앞차가 가까워지면 크루즈ON.

- **값을 높이면:** 적용 거리 또는 간격이 커집니다.
- **값을 낮추면:** 거리 또는 간격이 줄어듭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 출발·가속 페달·선행차 조건에서 한 항목씩 변경하고, 크루즈 활성화 시점과 설정 속도를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END CruiseOnDist -->

<!-- CARROT:SETTING:END CruiseOnDist -->
