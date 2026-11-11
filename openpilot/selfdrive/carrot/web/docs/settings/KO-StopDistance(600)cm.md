<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_STOPGO" param="StopDistanceCarrot" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# StopDistance(600)cm

**메뉴:** 주행 제어 \> 크루즈·차간 \> 정차·재출발

---

<!-- CARROT:SETTING:BEGIN StopDistanceCarrot -->
<a id="StopDistanceCarrot"></a>

## StopDistance(600)cm

`StopDistanceCarrot`

정지위치 \* 0.8

<!-- CARROT:AUTO:BEGIN StopDistanceCarrot -->
<!-- CARROT:AUTO:SOURCE facts="cda4ed210c1cc88c5be3c4061f257045895de3b652c19bb4e0b8f01af6bb2320" semantic="828f04295b09ba58b2345b32de89023747b2e835cd5f40e45378caea5d4fc7d8" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `600cm`
- **범위:** `400cm` ~ `1000cm`
- **변경 단위:** `10`
- **표시 단위:** `cm`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 정차·재출발
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END StopDistanceCarrot -->

<!-- CARROT:MANUAL:BEGIN StopDistanceCarrot -->
<!-- CARROT:REVIEW reviewed-for="828f04295b09ba58b2345b32de89023747b2e835cd5f40e45378caea5d4fc7d8" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

종방향 MPC가 선행차와 정지 장애물에 사용하는 기본 정지 여유 거리입니다.

- **값을 높이면:** 목표 정지·추종 여유가 커집니다.
- **값을 낮추면:** 목표 여유가 줄어듭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 선행차 정지·출발 조건에서 한 항목씩 조정하고, 최종 정지 위치와 재출발 반응을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 잘못된 값은 조향 또는 가감속의 안정성과 승차감을 떨어뜨릴 수 있습니다. 한 항목씩 작은 단계로 조정하고 이상이 있으면 기본값으로 복구합니다.
<!-- CARROT:NOTICE:END -->

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END StopDistanceCarrot -->

<!-- CARROT:SETTING:END StopDistanceCarrot -->
