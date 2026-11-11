<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_TRAFFIC" param="TrafficLightDetectMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 신호감지 기능

**메뉴:** 주행 제어 \> 속도·감속 \> 신호감지

---

<!-- CARROT:SETTING:BEGIN TrafficLightDetectMode -->
<a id="TrafficLightDetectMode"></a>

## 신호감지 기능

`TrafficLightDetectMode`

0:신호감지안함 1:신호정지만 감지 2:신호정지/출발 모두

<!-- CARROT:AUTO:BEGIN TrafficLightDetectMode -->
<!-- CARROT:AUTO:SOURCE facts="8e6470e97f1bec4d039f79ad0a010a13095d2b5c21a5fb509e4170e05cf2859c" semantic="fd5f942d148667ec255b07cf1ad246adcea8b41be25a134af644d9c7d0792e99" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `2`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 신호감지
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TrafficLightDetectMode -->

<!-- CARROT:MANUAL:BEGIN TrafficLightDetectMode -->
<!-- CARROT:REVIEW reviewed-for="fd5f942d148667ec255b07cf1ad246adcea8b41be25a134af644d9c7d0792e99" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 신호감지안함
- `1` — 신호정지만 감지
- `2` — 신호정지/출발 모두
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

신호가 명확히 보이는 동일 교차로에서 감지·정지·출발 시점과 정지 위치를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 신호 감지는 보조 기능이며 실제 신호와 교통 상황을 운전자가 직접 확인해야 합니다.
<!-- CARROT:NOTICE:END -->

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TrafficLightDetectMode -->

<!-- CARROT:SETTING:END TrafficLightDetectMode -->
