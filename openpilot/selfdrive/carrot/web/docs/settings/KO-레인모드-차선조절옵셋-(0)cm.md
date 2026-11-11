<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANEMODE" param="AdjustLaneOffset" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 레인모드: 차선조절옵셋 (0)cm

**메뉴:** 주행 제어 \> 차량 조향 \> 레인모드

---

<!-- CARROT:SETTING:BEGIN AdjustLaneOffset -->
<a id="AdjustLaneOffset"></a>

## 레인모드: 차선조절옵셋 (0)cm

`AdjustLaneOffset`

도로경계쪽/커브안쪽으로 보정합니다.

<!-- CARROT:AUTO:BEGIN AdjustLaneOffset -->
<!-- CARROT:AUTO:SOURCE facts="0aa44a4649c9d58885cccb487bd27f6b0ed5446cdb74bb4300a0261cd4443914" semantic="919b501dd31d3d3f258b212892e8fb3d2436b4872e6787e10d4fb65765fa6cfb" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0cm`
- **범위:** `0cm` ~ `500cm`
- **변경 단위:** `10`
- **표시 단위:** `cm`
- **메뉴:** 주행 제어 \> 차량 조향 \> 레인모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AdjustLaneOffset -->

<!-- CARROT:MANUAL:BEGIN AdjustLaneOffset -->
<!-- CARROT:REVIEW reviewed-for="919b501dd31d3d3f258b212892e8fb3d2436b4872e6787e10d4fb65765fa6cfb" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

도로경계쪽/커브안쪽으로 보정합니다.

- **값을 높이면:** 보정값이 양의 방향으로 이동합니다.
- **값을 낮추면:** 보정값이 음의 방향으로 이동합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 차선과 커브를 반복 주행하며 한 항목씩 조정하고, 경로 추종·조향 속도·부드러움을 함께 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 잘못된 값은 조향 또는 가감속의 안정성과 승차감을 떨어뜨릴 수 있습니다. 한 항목씩 작은 단계로 조정하고 이상이 있으면 기본값으로 복구합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AdjustLaneOffset -->

<!-- CARROT:SETTING:END AdjustLaneOffset -->
