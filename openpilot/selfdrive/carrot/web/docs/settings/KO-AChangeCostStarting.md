<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_STOPGO" param="AChangeCostStarting" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AChangeCostStarting

**메뉴:** 주행 제어 \> 크루즈·차간 \> 정차·재출발

---

<!-- CARROT:SETTING:BEGIN AChangeCostStarting -->
<a id="AChangeCostStarting"></a>

## AChangeCostStarting

`AChangeCostStarting`

출발가속도제한, 0:빠른가속도

<!-- CARROT:AUTO:BEGIN AChangeCostStarting -->
<!-- CARROT:AUTO:SOURCE facts="3ab6304ff512960839cc74428b72fee8b008468a11108b475dc1ab39db483661" semantic="66fd2bf8a16210234cb0ec52d03ef432cc413d2ec880fd815f8fb436da528c88" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `10`
- **범위:** `0` ~ `200`
- **변경 단위:** `10`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 정차·재출발
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AChangeCostStarting -->

<!-- CARROT:MANUAL:BEGIN AChangeCostStarting -->
<!-- CARROT:REVIEW reviewed-for="66fd2bf8a16210234cb0ec52d03ef432cc413d2ec880fd815f8fb436da528c88" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

출발 구간에서 가속도 변화 억제 비용을 조정합니다.

- **값을 높이면:** 출발 시 가속도 변화 억제가 커집니다.
- **값을 낮추면:** 출발 가속을 더 빠르게 허용합니다.
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
<!-- CARROT:MANUAL:END AChangeCostStarting -->

<!-- CARROT:SETTING:END AChangeCostStarting -->
