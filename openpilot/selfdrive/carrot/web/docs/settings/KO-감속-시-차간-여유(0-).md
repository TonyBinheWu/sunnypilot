<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_GAP" param="TFollowDecelBoost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 감속 시 차간 여유(0%)

**메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리

---

<!-- CARROT:SETTING:BEGIN TFollowDecelBoost -->
<a id="TFollowDecelBoost"></a>

## 감속 시 차간 여유(0%)

`TFollowDecelBoost`

감속 강도에 따라 기준 목표 간격에 추가 여유를 한 번만 더합니다. 감속이 지속되어도 같은 보정이 반복 누적되지 않습니다. 값이 클수록 여유가 커지고, 감속이 약해지면 추가 여유를 서서히 줄입니다. 0%는 추가 여유를 끄며 이미 적용된 여유는 서서히 해제됩니다. 감속 중 기준 차간 축소 보류는 유지합니다.

<!-- CARROT:AUTO:BEGIN TFollowDecelBoost -->
<!-- CARROT:AUTO:SOURCE facts="3b503844092eb188a7454f4a9ecbb5a25ad990c492ef2354d7ac4927460ad5a0" semantic="a003496b606637110045bb4c8096e6fd7af91b9b8c2778f41be61772125c46ca" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0%`
- **범위:** `0%` ~ `100%`
- **변경 단위:** `10`
- **표시 단위:** `%`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowDecelBoost -->

<!-- CARROT:MANUAL:BEGIN TFollowDecelBoost -->
<!-- CARROT:REVIEW reviewed-for="a003496b606637110045bb4c8096e6fd7af91b9b8c2778f41be61772125c46ca" reviewed-at="2026-09-09T08:56:50.246823+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

감속 강도에 따라 기준 목표 차간에 여유를 한 번만 더하며, 지속 감속에서도 같은 보정을 반복 누적하지 않습니다. 높이면 추가 여유가 커지고 낮추면 작아집니다.

감속이 약해지면 추가 여유를 서서히 줄이고, 감속이 강해지면 추가 여유를 바로 갱신합니다. 사용을 꺼도 이미 적용된 여유는 서서히 해제되며 감속 중 기준 차간 축소 보류는 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

감속 중 간격 확보 성향을 조정할 때 사용합니다. 값의 변경은 기본 차간 설정 자체를 바꾸지 않습니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:MANUAL:END TFollowDecelBoost -->

<!-- CARROT:SETTING:END TFollowDecelBoost -->
